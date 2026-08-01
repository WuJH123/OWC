import csv, numpy as np
from pathlib import Path
import matplotlib as mpl, matplotlib.pyplot as plt
src=Path('results/dba_Topt_efficiency_1500.csv')
D=[]
with src.open(newline='') as f:
 for r in csv.DictReader(f): D.append([float(r[k]) for k in ['d','b','a','Topt','efficiency']])
D=np.asarray(D); d,b,a,topt,eff=D.T

def rank(x):
 o=np.argsort(x,kind='mergesort'); rr=np.empty(len(x)); rr[o]=np.arange(len(x)); v=x[o]; i=0
 while i<len(v):
  j=i+1
  while j<len(v) and v[j]==v[i]: j+=1
  rr[o[i:j]]=(i+j-1)/2; i=j
 return rr
rho=np.corrcoef(np.vstack([rank(D[:,i]) for i in range(5)]))
mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],'font.size':6.3,'axes.labelsize':6.5,'xtick.labelsize':5.5,'ytick.labelsize':5.5,'axes.linewidth':.6,'pdf.fonttype':42,'svg.fonttype':'none','savefig.bbox':'tight','savefig.pad_inches':.025})
def panel(ax,l):
 ax.text(-.14,1.05,l,transform=ax.transAxes,fontsize=8,fontweight='bold',va='top'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.tick_params(length=2.5,width=.6,direction='out')
def curve(ax,x,y,label,r):
 e=np.quantile(x,np.linspace(0,1,13)); xx=[]; med=[]; lo=[]; hi=[]
 for i in range(12):
  m=(x>=e[i]) & ((x<=e[i+1]) if i==11 else (x<e[i+1])); xx.append(np.median(x[m])); med.append(np.median(y[m])); lo.append(np.quantile(y[m],.25)); hi.append(np.quantile(y[m],.75))
 ax.fill_between(xx,lo,hi,alpha=.25,lw=0); ax.plot(xx,med,'o-',ms=2.6,lw=1.1); ax.set(xlabel=label,ylabel=r'Optimal wave period, $T_{opt}$ (s)'); ax.text(.97,.06,rf'$\rho_s$ = {r:.2f}',transform=ax.transAxes,ha='right')
def heat(ax,x,y,z,xbins=10,ybins=10):
 xe=np.quantile(x,np.linspace(0,1,xbins+1)); ye=np.quantile(y,np.linspace(0,1,ybins+1)); H=np.full((ybins,xbins),np.nan)
 for i in range(xbins):
  for j in range(ybins):
   m=(x>=xe[i]) & ((x<=xe[i+1]) if i==xbins-1 else (x<xe[i+1])) & (y>=ye[j]) & ((y<=ye[j+1]) if j==ybins-1 else (y<ye[j+1]))
   if m.sum()>=3: H[j,i]=np.median(z[m])
 return ax.pcolormesh(xe,ye,H,cmap='viridis',vmin=topt.min(),vmax=topt.max(),shading='flat')
out=Path('results/figures'); out.mkdir(parents=True,exist_ok=True)
fig,axs=plt.subplots(2,2,figsize=(7.2,5.15))
curve(axs[0,0],d,topt,'Draft, d',rho[0,3]); panel(axs[0,0],'a')
curve(axs[0,1],b,topt,'Chamber width, b',rho[1,3]); panel(axs[0,1],'b')
curve(axs[1,0],a,topt,'Opening ratio, a',rho[2,3]); panel(axs[1,0],'c')
im=heat(axs[1,1],d,b,topt); axs[1,1].set(xlabel='Draft, d',ylabel='Chamber width, b'); panel(axs[1,1],'d'); cb=fig.colorbar(im,ax=axs[1,1],fraction=.047,pad=.03); cb.set_label(r'Median $T_{opt}$ (s)')
fig.subplots_adjust(wspace=.31,hspace=.34); fig.savefig(out/'Fig4_Topt_geometry_relationships.svg'); fig.savefig(out/'Fig4_Topt_geometry_relationships.pdf'); plt.close(fig)
q=np.quantile(a,[0,1/3,2/3,1])
fig,axs=plt.subplots(1,3,figsize=(7.2,2.55),sharex=True,sharey=True)
for i,ax in enumerate(axs):
 m=(a>=q[i]) & ((a<=q[i+1]) if i==2 else (a<q[i+1])); im=heat(ax,d[m],b[m],topt[m],8,8); ax.set_xlabel('Draft, d'); ax.set_title([r'Low $a$',r'Intermediate $a$',r'High $a$'][i]+f'\n{q[i]:.4f}–{q[i+1]:.4f}',fontsize=6.3,fontweight='normal'); panel(ax,chr(97+i))
 if i==0: ax.set_ylabel('Chamber width, b')
cb=fig.colorbar(im,ax=axs.ravel().tolist(),fraction=.025,pad=.025); cb.set_label(r'Median $T_{opt}$ (s)'); fig.subplots_adjust(left=.08,right=.90,bottom=.20,top=.82,wspace=.16)
fig.savefig(out/'Fig5_Topt_d_b_by_opening_ratio.svg'); fig.savefig(out/'Fig5_Topt_d_b_by_opening_ratio.pdf'); plt.close(fig)
