

      SUBROUTINE frun_CEMANEIGE(
                                 !inputs
     &                             LInputs              , ! [integer] length of input and output series
     &                             InputsPrecip         , ! [double]  input series of total precipitation [mm]
     &                             InputsFracSolidPrecip, ! [double]  input series of fraction of solid precipitation [0-1]
     &                             InputsTemp           , ! [double]  input series of air mean temperature [degC]
     &                             MeanAnSolidPrecip    , ! [double]  value of annual mean solid precip [mm/y]
     &                             NParam               , ! [integer] number of model parameter
     &                             Param                , ! [double]  parameter set
     &                             NStates              , ! [integer] number of state variables used for model initialising = 2
     &                             StateStart           , ! [double]  state variables used when the model run starts
     &                             NOutputs             , ! [integer] number of output series
     &                             IndOutputs           , ! [integer] indices of output series
                                 !outputs
     &                             Outputs              , ! [double]  output series
     &                             StateEnd             ) ! [double]  state variables at the end of the model run


      !DEC$ ATTRIBUTES DLLEXPORT :: frun_CemaNeige


      Implicit None
      !### input and output variables
      integer, intent(in) :: LInputs,NParam,NStates,NOutputs
      doubleprecision, intent(in) :: MeanAnSolidPrecip
      doubleprecision, dimension(LInputs) :: InputsPrecip
      doubleprecision, dimension(LInputs) :: InputsFracSolidPrecip
      doubleprecision, dimension(LInputs) :: InputsTemp
      doubleprecision, dimension(NParam)  :: Param
      doubleprecision, dimension(NStates) :: StateStart
      doubleprecision, dimension(NStates) :: StateEnd
      integer, dimension(NOutputs) :: IndOutputs
      doubleprecision, dimension(LInputs,NOutputs) :: Outputs

      !parameters, internal states and variables
      doubleprecision CTG,Kf
      doubleprecision G,eTG,PliqAndMelt
      doubleprecision Tmelt,Gthreshold,MinSpeed
      doubleprecision Pliq,Psol,Gratio,PotMelt,Melt
      integer I,K

      !--------------------------------------------------------------
      !Initialisations
      !--------------------------------------------------------------

      !initilisation des constantes
      Tmelt=0.
      Gthreshold=0.9*MeanAnSolidPrecip
      MinSpeed=0.1

      !initilisation of model states using StateStart
      G=StateStart(1)
      eTG=StateStart(2)
      PliqAndMelt=0.

      !setting parameter values
      CTG=Param(1)
      Kf=Param(2)

      !initialisation of model outputs
c      StateEnd = -999.999 !initialisation made in R
c      Outputs = -999.999  !initialisation made in R



      !--------------------------------------------------------------
      !Time loop
      !--------------------------------------------------------------
      DO k=1,LInputs

        !SolidPrecip and LiquidPrecip
        Pliq=(1-InputsFracSolidPrecip(k))*InputsPrecip(k)
        Psol=InputsFracSolidPrecip(k)*InputsPrecip(k)

        !Snow pack volume before melt
        G=G+Psol

        !Snow pack thermal state before melt
        eTG=CTG*eTG + (1-CTG)*InputsTemp(k)
        IF(eTG.GT.0.) eTG=0.

        !Potential melt
        IF(eTG.EQ.0..AND.InputsTemp(k).GT.Tmelt) THEN
          PotMelt=Kf*(InputsTemp(k)-Tmelt)
          IF(PotMelt.GT.G) PotMelt=G
        ELSE
          PotMelt=0.
        ENDIF

        !Gratio
        IF(G.LT.Gthreshold) THEN
          Gratio=G/Gthreshold
        ELSE
          Gratio=1.
        ENDIF

        !Actual melt
        Melt=((1-MinSpeed)*Gratio+MinSpeed)*PotMelt

        !Update of snow pack volume
        G=G-Melt

        !Update of Gratio
        IF(G.LT.Gthreshold) THEN
          Gratio=G/Gthreshold
        ELSE
          Gratio=1.
        ENDIF

        !Water volume to pass to the hydrological model
        PliqAndMelt=Pliq+Melt

        !Storage of outputs
        DO I=1,NOutputs
          IF(IndOutputs(I).EQ.1) Outputs(k,I)=Pliq
          IF(IndOutputs(I).EQ.2) Outputs(k,I)=Psol
          IF(IndOutputs(I).EQ.3) Outputs(k,I)=G
          IF(IndOutputs(I).EQ.4) Outputs(k,I)=eTG
          IF(IndOutputs(I).EQ.5) Outputs(k,I)=Gratio
          IF(IndOutputs(I).EQ.6) Outputs(k,I)=PotMelt
          IF(IndOutputs(I).EQ.7) Outputs(k,I)=Melt
          IF(IndOutputs(I).EQ.8) Outputs(k,I)=PliqAndMelt
          IF(IndOutputs(I).EQ.9) Outputs(k,I)=InputsTemp(k)
        ENDDO

      ENDDO

      StateEnd(1)=G
      StateEnd(2)=eTG

      RETURN

      ENDSUBROUTINE

