select
 case   
    when (TESTNAME_NF like '%LTTC%')                       then 'LTTC'
    when (TESTNAME_NF like '%CHVQK%')                       then 'CHVQK'
    when (MODULE like '%PCH%')                             then 'PCH'
    when (MODULE like 'LBG%')                              then 'PCH'
    when (MODULE like '%_FVMIN%')                          then 'BINNING'
    when (MODULE like '%_INTERP%')                         then 'BINNING'
    when (MODULE like '%YBS_VP%')                          then 'BINNING'
    when (MODULE like '%_UPS%')                            then 'BINNING'
    when (MODULE like '%_LICENSE%')                        then 'BINNING'
    when (MODULE like '%CACHE%')                           then 'CACHE'
    when (MODULE like '%REPAIR%')                          then 'CACHE'
    when (MODULE like '%_FIVR%')                           then 'FIVR'
    when (MODULE like '%_PMAX%')                           then 'FIVR'
    when (MODULE like '%_VDAC%')                           then 'FIVR'
    when (MODULE like '%FUS_%')                            then 'FUSE'
    when (MODULE like '%SBFT%')                           then 'FUNC'
    when (MODULE like '%DRNG%')                           then 'FUNC'
    when (MODULE like '%MIO%')                             then 'MIO'
    when (MODULE like '%ADPLL%')                            then 'PLL'
    when (MODULE like '%LCPLL%')                            then 'PLL'
    when (MODULE like '%PWR%')                            then 'POWER'
    when (MODULE like '%_KTI%')                            then 'SIO'
    when (MODULE like '%_PCIE%')                          then 'SIO'
    when (MODULE like '%_BSCAN%')                           then 'SIO'
    when (MODULE like '%_LEAKAGE%')                           then 'SIO'
    when (MODULE like '%_UNIPHYBG%')                        then 'SIO'
    when (MODULE like '%SCAN%')                           then 'SCAN'
    when (MODULE like 'PTH_CTRS%')                         then 'THERMAL'
    when (MODULE like 'PTH_DTS%')                          then 'THERMAL'
    when (MODULE like 'PTH_SOT%')                          then 'THERMAL'
    when (MODULE like 'PTH_THRSOAK%')                      then 'THERMAL'
    else 'TPI' end as SCRUM,
    
 MODULE,TESTNAME_NF,
 average(ITIME_MAIN + ITIME_PRE) *  count (distinct Visual_ID) /    SAMPLESIZE Weighted_AVE,
 SAMPLESIZE SampledUnits,
 count (distinct Visual_ID) TestSampled,
 average(ITIME_MAIN + ITIME_PRE) TT_Average,
 max(ITIME_MAIN + ITIME_PRE) TT_Max,
 min(ITIME_MAIN + ITIME_PRE) TT_Min,
 LOT,OPERATION,DevRevStep,SUMRY,PROGRAM_NAME
 from 
 (
 select
       TS.LOT
      ,TS.OPERATION
      ,TS.DevRevStep
      ,TS.SUMMARY_NUM||TS.Summary_Letter SUMRY
      ,TS.Program_Or_BI_Recipe_Name PROGRAM_NAME
      ,TS.Total_Good
      ,AU.Visual_ID
      ,OREPLACE(OREPLACE(DTB.Sort_Lot||'_'||DTB.Sort_Wafer_Id||'_'||DTB.Sort_X_Location||'_'||DTB.Sort_Y_Location,' ',''),'.','') as ULT
      ,DTB.Unit_Interface_Bin as IBIN
      ,DTB.Unit_Functional_Bin as  FBIN
      ,DTB.Unit_DATA_BIN as DATABIN
      ,DT.TEST_TIME
      --,TIL.TEST_NAME
      ,SUBSTR(TIL.TEST_NAME,   INSTR(TIL.TEST_NAME,'_')+1     , INSTR(TIL.TEST_NAME,'::')   -  INSTR(TIL.TEST_NAME,'_') -1 )  MODULE
      ,SUBSTR(TIL.TEST_NAME,   INSTR(TIL.TEST_NAME,'::')+2  ) TESTNAME_NF
 	 ,OREPLACE(OREPLACE(OREPLACE(PR.String_Result, 'MS_MAIN',''),'PRE_',''),'MS','') TIMES
 	 ,CAST(SUBSTR(OREPLACE(OREPLACE(OREPLACE(PR.String_Result, 'MS_MAIN',''),'PRE_',''),'MS',''),0,INSTR(OREPLACE(OREPLACE(OREPLACE(PR.String_Result, 'MS_MAIN',''),'PRE_',''),'MS',''),'_'))  AS DECIMAL(9,0))ITIME_PRE
 	 ,CAST(SUBSTR(OREPLACE(OREPLACE(OREPLACE(PR.String_Result, 'MS_MAIN',''),'PRE_',''),'MS',''),INSTR(OREPLACE(OREPLACE(OREPLACE(PR.String_Result, 'MS_MAIN',''),'PRE_',''),'MS',''),'_')+1) AS DECIMAL(9,0))ITIME_MAIN
         from
                 MDS_LOT_OPER_TESTING_SESSION TS,
                 MDS_UNIT_TESTING DT,
                 MDS_UNIT_TESTING_BINS DTB,
                 MDS_ASSEMBLED_UNIT AU,
                 MDS_Test_In_Lots TIL,
                 MDS_Unit_String_Test_Result PR
         where
   TS.lot in ('CHANGE_ME')
   and TS.OPERATION in ('6262')
                 and DT.LATO_Start_WW = TS.LATO_Start_WW
                 and DT.Lot = TS.Lot
                 and DT.Operation = TS.Operation
                 and DT.LOTS_Seq_Key = TS.LOTS_Seq_Key
                 and DTB.LATO_Start_WW = DT.LATO_Start_WW
                 and DTB.Lot = DT.Lot
                 and DTB.Operation = DT.Operation
                 and DTB.LOTS_Seq_Key = DT.LOTS_Seq_Key
                 and DTB.Unit_Testing_Seq_Key =  DT.Unit_Testing_Seq_Key
                 and DTB.SubStructure_ID = 'UNIT'
                 and DTB.Unit_Interface_Bin < 7
                 and AU.Assembled_Unit_Seq_Key = DTB.Assembled_Unit_Seq_Key
                 and TS.LATO_Start_WW = TIL.LATO_Start_WW
                 and TS.Lot = TIL.Lot
                 and TS.LOTS_Seq_Key = TIL.LOTS_Seq_Key
                 and TS.LOTS_LATEST_FLAG = 'Y'
                 and PR.LATO_Start_WW          = DT.LATO_Start_WW
                 and PR.Lot                    = DT.Lot
                 and PR.LOTS_Seq_Key           = DT.LOTS_Seq_Key
                 and PR.Unit_Testing_Seq_Key   = DT.Unit_Testing_Seq_Key
                 and PR.Test_In_LOTS_Seq_Key   = TIL.Test_In_LOTS_Seq_Key
                 and TIL.Test_Name like '%TESTTIME%'
                 and PR.String_Result like 'PRE_%MS_MAIN%MS'
 ) T1,
 (
 select TS.lot SLOT,TS.OPERATION SOPERATION,TS.SUMMARY_NUM||TS.Summary_Letter SSUMRY, count(distinct AU.Visual_ID) SAMPLESIZE
         from
                 MDS_LOT_OPER_TESTING_SESSION TS,
                 MDS_UNIT_TESTING DT,
                 MDS_ASSEMBLED_UNIT AU,
                  MDS_UNIT_TESTING_BINS DTB,
                 MDS_Test_In_Lots TIL,
                 MDS_Unit_String_Test_Result PR
         where
   TS.lot in ('CHANGE_ME')
   and TS.OPERATION in ('6262')
                 and DT.LATO_Start_WW = TS.LATO_Start_WW
                 and DT.Lot = TS.Lot
                 and DT.Operation = TS.Operation
                 and DT.LOTS_Seq_Key = TS.LOTS_Seq_Key
                 and DTB.LATO_Start_WW = DT.LATO_Start_WW
                 and DTB.Lot = DT.Lot
                 and DTB.Operation = DT.Operation
                 and DTB.LOTS_Seq_Key = DT.LOTS_Seq_Key
                 and DTB.Unit_Testing_Seq_Key =  DT.Unit_Testing_Seq_Key
                 and DTB.SubStructure_ID = 'UNIT'
                 and DTB.Unit_Interface_Bin < 7
                 and AU.Assembled_Unit_Seq_Key = DTB.Assembled_Unit_Seq_Key
                 and TS.LATO_Start_WW = TIL.LATO_Start_WW
                 and TS.Lot = TIL.Lot
                 and TS.LOTS_Seq_Key = TIL.LOTS_Seq_Key
                 and TS.LOTS_LATEST_FLAG = 'Y'
                 and PR.LATO_Start_WW          = DT.LATO_Start_WW
                 and PR.Lot                    = DT.Lot
                 and PR.LOTS_Seq_Key           = DT.LOTS_Seq_Key
                 and PR.Unit_Testing_Seq_Key   = DT.Unit_Testing_Seq_Key
                 and PR.Test_In_LOTS_Seq_Key   = TIL.Test_In_LOTS_Seq_Key
                and TIL.Test_Name like '%TESTTIME%'
                and PR.String_Result like 'PRE_%MS_MAIN%MS'
 			   
 			   group by TS.lot,TS.OPERATION,TS.SUMMARY_NUM||TS.Summary_Letter
 ) SAMPLED
 where 
 	    LOT       = SLOT
 	and OPERATION = SOPERATION
 	and SUMRY     = SSUMRY
 	
 group by LOT, OPERATION,DevRevStep,SUMRY,PROGRAM_NAME,MODULE,TESTNAME_NF,SAMPLED.SAMPLESIZE
 order by LOT, OPERATION,DevRevStep,SUMRY,PROGRAM_NAME,SCRUM,MODULE,TESTNAME_NF