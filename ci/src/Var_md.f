C **************************************************
C 												
C   This is a module for declaring general variables  
C *************************************************				
C
       MODULE MVar_mod
	IMPLICIT REAL*8 (A-H,O-Z)
C
	REAL*8 TANKL,TANKH,Coetankl,DampL,H,hin,AZG1,p1(4),ptime1,ESIZE,
     1 p2(4),ptime2,ptime,AGZ2,ptime3,p3(4),ptime4,p4(4),ptime5,p5(4),
     1      AGZ3,AGZ4,AGZ5
            
	REAL*8 DENS,Cdm1,Cdm2,Cdm3,Cdm4,Cdm5,D,ad1,ad2,ad3,ad4,ad5,
     1    Gap1,Gap2,Gap3,Gap4,Gap5,
     1      bd1,bd2,bd3,bd4,bd5,ddm1,ddm2,ddm3,ddm4,ddm5,
     1      udt,udt1,udt2,udt3,udt4,udt5,RATIO,px1,pz1,my1,
     1  dv1,dv2,dv3,dv4,dv5,
     1       vt1,vt10,vt2,vt20,vt3,vt30,vt4,vt40,vt5,vt50
      REAL*8 sum1,sum2,sum3,sum4,sum5,Ew !!!
      REAL*8 EP1,EP2,EP3,EP4,EP5 !!!
      REAL*8 ptimearray11(200),ptimearray12(200),ptimearray13(200),
     1      ptimearray14(200),
     1 ptimearray21(200),
     1ptimearray22(200),ptimearray23(200),ptimearray24(200),
     1 ptimearray31(200),      
     1ptimearray32(200),ptimearray33(200),ptimearray34(200),
     1 ptimearray41(200),      
     1ptimearray42(200),ptimearray43(200),ptimearray44(200),
     1 ptimearray51(200),      
     1ptimearray52(200),ptimearray53(200),ptimearray54(200)
      
      
      REAL*8 Zttarray11(200),Zttarray12(200),Zttarray13(200),
     1      Zttarray14(200),Zttarray21(200),Zttarray22(200),
     1      Zttarray23(200),Zttarray24(200),Zttarray31(200),      
     1      Zttarray32(200),Zttarray33(200),Zttarray34(200),
     1 Zttarray41(200),      
     1      Zttarray42(200),Zttarray43(200),Zttarray44(200),
     1  Zttarray51(200),      
     1      Zttarray52(200),Zttarray53(200),Zttarray54(200)
      REAL*8 ZttOK1,ZttOK2,ZttOK3,ZttOK4,ZttOK5,
     1 ptimeOK1,ptimeOK2,ptimeOK3,ptimeOK4,ptimeOK5
      
	REAL*8 FC,FT
	REAL*8 DNEF12
      REAL*8 FDAMP2,FDAMP3,FDAMP4,FDAMP5,FDAMP6
	INTEGER NNPP,NEF10,NEF11,NEF12,NM
	Integer NEX,NEZ,NNX,NNZ,NNTX,NNTZ,NL,NEZ2,NNTZ2
	Integer NNF,NNI,NEF,NEI,NNT,NET
	Integer LT,NT,NTIME,Nsmooth,MWK
      Integer ok1,ok2,ok3,ok4,M_s,IIII

	REAL*8  AXX,AYY

	PARAMETER (NE0=2000, NN0=4000,NF0=2000,MWK=20)
C 
       DIMENSION  XE(NE0,3),ZE(NE0,3),DXE(NE0,3),DZE(NE0,3),AREA(NE0)
	 DIMENSION  XZ(NN0,2),XZ0(NN0,2),ANGLE8(NN0),XZ1(NN0,2),
	1       az1(4),az2(4),az3(4),az4(4),az5(4)
       DIMENSION NCN(NE0),NCNE(NE0,3),NCON(NE0,3),
	1  NODELE(NN0,10),NODNOE(NN0),NODELJ(NN0,10),PO(NN0)
  	DIMENSION NMULTI(NN0),NELE(NN0,10),NLOC(NN0,10)
C
       DIMENSION SAMB(NE0,4,0:3),SAMBXZ(NE0,4,2),DSAMB(NE0,4,3)
	 DIMENSION SAMBSJ(NE0,4,3),AH1(1000), AH2(1000),AH3(1000),
     1AH4(1000),AH5(1000)
	 DIMENSION HEIGHT(NF0),PFREEN(NF0),HX(NF0),PXZ(NF0,2),PXYZ8(NN0,2)
       
       DIMENSION s_o(1000),A_n(1000),w_n(1000),WKK(1000),e(1000),
     1Cg(1000)


	 DIMENSION BMATA(NN0),AMATA(NN0,NN0)
       INTEGER IWFLAG,MMT
	 INTEGER Nwavekind
	 CHARACTER*13 NAME,NAME1
	 CHARACTER*6 FIRST

	 REAL*8 BETA,AMP,TPER,W1,W2,WK(MWK),WLONG,CELE,SLOPE,H_s 
       REAL*8 G,RHO,PI,WK1,WK2,w_max,w_min,dm,gama,sigma_a,sigma_b     
	 REAL*8 T,TSTEP,DELTL,DELTB,DELTH
       REAL*8 DELTL1,DELTL2,DELTL3,DELTL4,DELTL5
       REAL*8 XC,ZC,U0,Tf,Wm,Tf1,w_w,sigma,bj,rand,E_1,sum_s

C   Bottom parameter
      REAL*8 Xd0, Xd1, Xd2, Xd3, slope1,slope2, 
     1       XF1,XF2,XF3,XF4,XF5,XF6,XF7,XF8,XF9,XF10,XF11,
     1       TANKH01, TankH02,TankH03,TankH04,TankH05

      INTEGER NEX1,NEX2,NEX3, NNTX1,NNTX2,NNTX3,NEB,NNB,En0,NEZ1,NNTZ1,
     1        NNB1,NNB2,NEB1,NEB2,NEB3,NEB4,NEB5,NNB3,NNB4,NNB5
	INTEGER NEX4,NEX5,NEX6,NNTX4,NNTX5,NNTX6, NNTXF1,NNTXF2,NNTXF3
      INTEGER NEX7,NEX8,NEX9,NNTX7,NNTX8,NNTX9, NNTXF4
      INTEGER NEX10,NEX11,NEX12,NNTX10,NNTX11,NNTX12, NNTXF5
      INTEGER NEX13,NEX14,NEX15,NNTX13,NNTX14,NNTX15, NNTXF6
	INTEGER NEF1,NEF2,NEF3,NEF4,NEF5,NEF6,n_1,ios

	DIMENSION XZd(1000,2)
      
          character(len=20) :: filename
          real, dimension(:), allocatable :: hy
          real ::  H_3


C      
      DATA G,PI,RHO,DENS/9.807,3.1415926535897930,
	1	               1023.0,1000.0/ 
C

       END MODULE MVar_mod

C
C =========================================
C  Varibles used in the Tri-pole transform 
C							  

       MODULE TRVar_mod

!	 INTEGER NOSAMP

!	 REAL*8 XYNOD(3,50),DXYNOD(6,50),SAMNOD(50,0:8)
       REAL*8 TRISI(50),TRIETA(50),TRIWIQ(50)

       END MODULE TRVar_mod
