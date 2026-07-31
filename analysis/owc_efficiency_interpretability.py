from __future__ import annotations
import argparse, json
from itertools import combinations
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor
import shap

SEED=20260731
Y='result_efficiencyOWC'
F=['wave_period','wave_amplitude','draft','front_wall_thickness','chamber_width','opening_ratio','quadratic_damping','artificial_damping']
S={'wave_period':'T','wave_amplitude':'A','draft':'d','front_wall_thickness':'tw','chamber_width':'b','opening_ratio':'a','quadratic_damping':'Cq','artificial_damping':'Ca'}
L={'wave_period':'Wave period, T','wave_amplitude':'Wave amplitude, A','draft':'Draft, d','front_wall_thickness':'Front-wall thickness, tw','chamber_width':'Chamber width, b','opening_ratio':'Opening ratio, a','quadratic_damping':'Quadratic damping, Cq','artificial_damping':'Artificial damping, Ca'}

def style():
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Liberation Sans','Arial','Helvetica','DejaVu Sans'],'font.size':6.5,'axes.labelsize':6.5,'xtick.labelsize':5.8,'ytick.labelsize':5.8,'legend.fontsize':5.8,'axes.linewidth':.6,'pdf.fonttype':42,'svg.fonttype':'none','savefig.bbox':'tight','savefig.pad_inches':.03})

def lab(ax,x): ax.text(-.13,1.05,x,transform=ax.transAxes,fontsize=8,fontweight='bold',va='top')
def save(fig,p): fig.savefig(p.with_suffix('.svg')); fig.savefig(p.with_suffix('.pdf')); fig.savefig(p.with_suffix('.png'),dpi=450); plt.close(fig)

def load_clean(path):
    raw=pd.read_csv(path); miss=[c for c in F+[Y] if c not in raw]
    if miss: raise ValueError(f'Missing: {miss}')
    audit=pd.DataFrame([{'variable':c,'n':raw[c].notna().sum(),'missing':raw[c].isna().sum(),'n_unique':raw[c].nunique(),'min':raw[c].min(),'p01':raw[c].quantile(.01),'median':raw[c].median(),'p99':raw[c].quantile(.99),'max':raw[c].max()} for c in F+[Y]])
    dup=raw.duplicated(F,keep='first'); d=raw.loc[~dup].copy(); q1,q3=d[Y].quantile([.25,.75]); fence=q3+1.5*(q3-q1); bad=(d[Y]<0)|(d[Y]>fence)
    anom=d.loc[bad,([c for c in ['case_id'] if c in d]+F+[Y])]; clean=d.loc[~bad].copy()
    quality={'raw_rows':len(raw),'raw_columns':raw.shape[1],'selected_missing_total':int(raw[F+[Y]].isna().sum().sum()),'duplicate_input_rows_removed':int(dup.sum()),'iqr_upper_fence':float(fence),'extreme_target_rows_removed':int(bad.sum()),'efficiency_gt_1_count_raw':int((raw[Y]>1).sum()),'efficiency_gt_1p05_count_raw':int((raw[Y]>1.05).sum()),'final_rows':len(clean)}
    return raw,clean,audit,anom,quality

def train(clean):
    X,y=clean[F],clean[Y]; Xt,Xu,yt,yu=train_test_split(X,y,test_size=.30,random_state=SEED); Xv,Xe,yv,ye=train_test_split(Xu,yu,test_size=.50,random_state=SEED)
    models={'Linear':LinearRegression(),'ExtraTrees':ExtraTreesRegressor(n_estimators=500,min_samples_leaf=2,n_jobs=-1,random_state=SEED),'XGBoost':XGBRegressor(n_estimators=1600,learning_rate=.03,max_depth=7,min_child_weight=3,subsample=.9,colsample_bytree=.9,reg_lambda=2,objective='reg:squarederror',n_jobs=-1,random_state=SEED,tree_method='hist')}
    rows=[]
    for n,m in models.items():
        m.fit(Xt,yt,**({'eval_set':[(Xv,yv)],'verbose':False} if n=='XGBoost' else {}))
        for sp,Xs,ys in [('validation',Xv,yv),('test',Xe,ye)]:
            p=m.predict(Xs); rows.append({'model':n,'split':sp,'R2':r2_score(ys,p),'RMSE':mean_squared_error(ys,p)**.5,'MAE':mean_absolute_error(ys,p)})
    xgb=models['XGBoost']; cv=cross_validate(xgb,X,y,cv=KFold(5,shuffle=True,random_state=SEED),scoring={'R2':'r2','RMSE':'neg_root_mean_squared_error','MAE':'neg_mean_absolute_error'},n_jobs=1)
    cvdf=pd.DataFrame({'fold':range(1,6),'R2':cv['test_R2'],'RMSE':-cv['test_RMSE'],'MAE':-cv['test_MAE']})
    return xgb,pd.DataFrame(rows),cvdf,Xe,ye

def shap_global(model,Xtest):
    Xs=Xtest.sample(min(4000,len(Xtest)),random_state=SEED); sv=np.asarray(shap.TreeExplainer(model).shap_values(Xs)); imp=pd.DataFrame({'feature':F,'mean_abs_shap':np.abs(sv).mean(0)}).sort_values('mean_abs_shap',ascending=False,ignore_index=True); return Xs,sv,imp

def fill(a):
    a=a.copy()
    for _ in range(20):
        if not np.isnan(a).any(): break
        old=a.copy()
        for i,j in np.argwhere(np.isnan(old)):
            n=old[max(0,i-1):i+2,max(0,j-1):j+2]
            if np.isfinite(n).any(): a[i,j]=np.nanmean(n)
    a[np.isnan(a)]=np.nanmean(a); return a

def ale2(model,X,f1,f2,bins=10):
    e1=np.unique(np.quantile(X[f1],np.linspace(0,1,bins+1))); e2=np.unique(np.quantile(X[f2],np.linspace(0,1,bins+1))); n1,n2=len(e1)-1,len(e2)-1
    i1=np.clip(np.searchsorted(e1,X[f1],side='right')-1,0,n1-1); i2=np.clip(np.searchsorted(e2,X[f2],side='right')-1,0,n2-1); lo1,hi1=e1[i1],e1[i1+1]; lo2,hi2=e2[i2],e2[i2+1]
    P=[]
    for a,b in [(lo1,lo2),(lo1,hi2),(hi1,lo2),(hi1,hi2)]:
        z=X.copy(); z[f1]=a; z[f2]=b; P.append(model.predict(z))
    delta=P[3]-P[2]-P[1]+P[0]; local=np.full((n1,n2),np.nan); counts=np.zeros((n1,n2),int)
    for i in range(n1):
        for j in range(n2):
            m=(i1==i)&(i2==j); counts[i,j]=m.sum(); local[i,j]=delta[m].mean() if m.any() else np.nan
    A=np.cumsum(np.cumsum(fill(local),0),1); W=counts.astype(float)
    for _ in range(50):
        d=W.sum(1); A-=np.divide((A*W).sum(1),d,out=np.zeros(n1),where=d>0)[:,None]; d=W.sum(0); A-=np.divide((A*W).sum(0),d,out=np.zeros(n2),where=d>0)[None,:]; A-=(A*W).sum()/W.sum()
    return {'x':(e1[:-1]+e1[1:])/2,'y':(e2[:-1]+e2[1:])/2,'edges1':e1,'edges2':e2,'ale':A,'counts':counts,'strength':float(np.sqrt((W*A*A).sum()/W.sum()))}

def ale_all(model,X):
    Xa=X.sample(min(10000,len(X)),random_state=SEED); out={}; rows=[]
    for a,b in combinations(F,2):
        r=ale2(model,Xa,a,b); out[(a,b)]=r; rows.append({'feature_1':a,'feature_2':b,'ale2_rms':r['strength'],'empty_cells':int((r['counts']==0).sum())})
    return out,pd.DataFrame(rows).sort_values('ale2_rms',ascending=False,ignore_index=True)

def envelope(clean):
    t=clean.copy(); t['_bin']=pd.qcut(t.wave_period,10,duplicates='drop'); rows=[]
    for _,g in t.groupby('_bin',observed=True):
        top=g[g[Y]>=g[Y].quantile(.90)]; r={'wave_period_mid':g.wave_period.median(),'efficiency_q90':g[Y].quantile(.90)}
        for f in ['draft','chamber_width','opening_ratio']:
            r[f+'_top_median']=top[f].median(); r[f+'_top_q25']=top[f].quantile(.25); r[f+'_top_q75']=top[f].quantile(.75); r[f+'_all_median']=g[f].median()
        rows.append(r)
    return pd.DataFrame(rows)

def figures(clean,model,metrics,Xtest,ytest,Xs,sv,imp,ales,rank,env,figdir):
    style(); figdir.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(1,2,figsize=(7.2,3.2)); p=model.predict(Xtest); ax[0].hexbin(ytest,p,gridsize=45,mincnt=1,cmap='viridis'); q=[min(ytest.min(),p.min()),max(ytest.max(),p.max())]; ax[0].plot(q,q,'k--',lw=.8); ax[0].set(xlabel='Simulated efficiency',ylabel='Predicted efficiency'); ax[0].text(.04,.96,f'$R^2$={r2_score(ytest,p):.4f}\nRMSE={mean_squared_error(ytest,p)**.5:.4f}\nMAE={mean_absolute_error(ytest,p):.4f}',transform=ax[0].transAxes,va='top'); lab(ax[0],'a')
    o=imp.sort_values('mean_abs_shap'); ax[1].barh(range(len(o)),o.mean_abs_shap,color='#4C78A8'); ax[1].set_yticks(range(len(o)),[L[x] for x in o.feature]); ax[1].set_xlabel('Mean |SHAP value|'); lab(ax[1],'b'); save(fig,figdir/'Fig1_surrogate_SHAP')
    pairs=[('wave_period','draft'),('wave_period','chamber_width'),('wave_period','opening_ratio')]; fig=plt.figure(figsize=(7.2,5.45)); gs=fig.add_gridspec(2,3,width_ratios=[1,1,.055],wspace=.42,hspace=.40); A=[fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1])]; cax=fig.add_subplot(gs[:,2]); top=rank.head(10).iloc[::-1]; A[0].barh(range(len(top)),top.ale2_rms,color='#4C78A8'); A[0].set_yticks(range(len(top)),[S[a]+' × '+S[b] for a,b in zip(top.feature_1,top.feature_2)]); A[0].set_xlabel('RMS second-order ALE'); lab(A[0],'a'); vmax=max(np.abs(ales[p]['ale']).max() for p in pairs); norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    last=None
    for ax,pair,letter in zip(A[1:],pairs,['b','c','d']):
        r=ales[pair]; z=np.ma.masked_where(r['counts']<20,r['ale']); last=ax.pcolormesh(r['edges1'],r['edges2'],z.T,cmap='RdBu_r',norm=norm,shading='flat'); ax.set(xlabel='Wave period, T',ylabel=L[pair[1]]); ax.text(.98,.03,f"RMS={r['strength']:.3f}",transform=ax.transAxes,ha='right',bbox={'facecolor':'white','edgecolor':'none','alpha':.8,'pad':1.2}); lab(ax,letter)
    fig.colorbar(last,cax=cax,label='Second-order ALE contribution to efficiency'); save(fig,figdir/'Fig2_second_order_ALE_period_geometry')
    fig,ax=plt.subplots(1,3,figsize=(7.2,2.65)); x=env.wave_period_mid.to_numpy();
    for a,(f,yl),letter in zip(ax,[('draft','Draft, d'),('chamber_width','Chamber width, b'),('opening_ratio','Opening ratio, a')],['a','b','c']):
        a.fill_between(x,env[f+'_top_q25'],env[f+'_top_q75'],color='#9ECAE1',alpha=.5); a.plot(x,env[f+'_top_median'],'o-',lw=1.1,ms=3.2,label='Top 10% efficiency'); a.plot(x,env[f+'_all_median'],'--',color='.45',lw=.9,label='All cases'); a.set(xlabel='Wave period, T',ylabel=yl); lab(a,letter)
    ax[0].legend(frameon=False); save(fig,figdir/'Fig3_high_efficiency_period_geometry_envelope')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--csv',required=True,type=Path); ap.add_argument('--out',default=Path('results'),type=Path); a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True); figdir=a.out/'figures'
    raw,clean,audit,anom,q=load_clean(a.csv); model,metrics,cv,Xtest,ytest=train(clean); Xs,sv,imp=shap_global(model,Xtest); ales,rank=ale_all(model,clean[F]); env=envelope(clean)
    audit.to_csv(a.out/'data_audit.csv',index=False); anom.to_csv(a.out/'excluded_extreme_cases.csv',index=False); metrics.to_csv(a.out/'model_metrics.csv',index=False); cv.to_csv(a.out/'xgboost_5fold_cv.csv',index=False); imp.to_csv(a.out/'shap_importance.csv',index=False); rank.to_csv(a.out/'ale2_interaction_ranking.csv',index=False); env.to_csv(a.out/'period_geometry_high_efficiency_envelope.csv',index=False)
    corr=pd.DataFrame([{'pair':'wave_period__'+f,'pearson_r':clean[['wave_period',f]].corr().iloc[0,1],'spearman_rho':clean[['wave_period',f]].corr(method='spearman').iloc[0,1]} for f in ['draft','chamber_width','opening_ratio']]); corr.to_csv(a.out/'period_geometry_input_correlations.csv',index=False)
    figures(clean,model,metrics,Xtest,ytest,Xs,sv,imp,ales,rank,env,figdir); t=metrics[(metrics.model=='XGBoost')&(metrics.split=='test')].iloc[0]; q['xgboost_test']={'R2':float(t.R2),'RMSE':float(t.RMSE),'MAE':float(t.MAE)}; q['xgboost_5fold_cv']={'R2_mean':float(cv.R2.mean()),'R2_sd':float(cv.R2.std(ddof=1))}; q['top_shap']=imp.to_dict('records'); q['top_ale2']=rank.head(10).to_dict('records'); (a.out/'summary.json').write_text(json.dumps(q,indent=2)); model.save_model(a.out/'xgboost_surrogate.ubj'); print(json.dumps(q,indent=2))
if __name__=='__main__': main()
