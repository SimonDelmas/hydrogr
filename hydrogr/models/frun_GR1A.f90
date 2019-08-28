SUBROUTINE frun_GR1A(LInputs, InputsPrecip, InputsPE, NParam, Param, NStates, StateStart, NOutputs, IndOutputs, Outputs, StateEnd)
!
!    LInputs      , ! [integer] length of input and output series&
!    InputsPrecip , ! [double] input series of total precipitation [mm/year]&
!    InputsPE     , ! [double] input series of potential evapotranspiration (PE) [mm/year]&
!    NParam       , ! [integer] number of model parameters&
!    Param        , ! [double] parameter set&
!    NStates      , ! [integer] number of state variables&
!    StateStart   , ! [double] state variables used when the model run starts (none here)&
!    NOutputs     , ! [integer] number of output series&
!    IndOutputs   , ! [integer] indices of output series&
!    Outputs      , ! [double] output series&
!    StateEnd       ! [double] state variables at the end of the model run (none here)


    !     !DEC$ ATTRIBUTES DLLEXPORT :: frun_GR1A

    Implicit None
    !     !### input and output variables
    integer, intent(in) :: LInputs, NParam, NStates, NOutputs
    doubleprecision, dimension(LInputs) :: InputsPrecip
    doubleprecision, dimension(LInputs) :: InputsPE
    doubleprecision, dimension(NParam) :: Param
    doubleprecision, dimension(NStates) :: StateStart
    doubleprecision, dimension(NStates) :: StateEnd
    integer, dimension(NOutputs) :: IndOutputs
    doubleprecision, dimension(LInputs, NOutputs) :: Outputs

    !     !parameters, internal states and variables
    integer NMISC
    parameter (NMISC = 3)
    doubleprecision MISC(NMISC)
    doubleprecision P0, P1, E1, Q
    integer I, K

    !     !--------------------------------------------------------------
    !     !Initializations
    !     !--------------------------------------------------------------

    !     !parameter values
    !     !Param(1) : PE adjustment factor [-]

    !     !initialization of model outputs
    Q = -999.999
    MISC = -999.999
    !      Outputs = -999.999  !initialization made in R



    !     !--------------------------------------------------------------
    !     !Time loop
    !     !--------------------------------------------------------------
    DO k = 2, LInputs
        P0 = InputsPrecip(k - 1)
        P1 = InputsPrecip(k)
        E1 = InputsPE(k)
        !        Q = -999.999
        !        MISC = -999.999
        !       !model run on one time step
        CALL MOD_GR1A(Param, P0, P1, E1, Q, MISC)
        !       !storage of outputs
        DO I = 1, NOutputs
            Outputs(k, I) = MISC(IndOutputs(I))
        ENDDO
    ENDDO

    RETURN

ENDSUBROUTINE


!################################################################################################################################




!**********************************************************************
SUBROUTINE MOD_GR1A(Param, P0, P1, E1, Q, MISC)
    ! Calculation of streamflow on a single time step with the GR1A model
    ! Inputs:
    !       Param  Vector of model parameters (Param(1) [-])
    !       P0     Value of rainfall during the previous time step [mm/year]
    !       P1     Value of rainfall during the current time step [mm/year]
    !       E1     Value of potential evapotranspiration during the current time step [mm/year]
    ! Outputs:
    !       Q      Value of simulated flow at the catchment outlet for the current time step [mm/year]
    !       MISC   Vector of model outputs for the time step [mm]
    !**********************************************************************
    Implicit None
    INTEGER NMISC, NParam
    PARAMETER (NMISC = 3)
    PARAMETER (NParam = 1)
    DOUBLEPRECISION Param(NParam)
    DOUBLEPRECISION MISC(NMISC)
    DOUBLEPRECISION P0, P1, E1, Q

    DOUBLEPRECISION tt ! speed-up

    ! Runoff
    !     ! speed-up
    tt = (0.7 * P1 + 0.3 * P0) / Param(1) / E1
    Q = P1 * (1. - 1. / SQRT(1. + tt * tt))
    !     ! Q=P1*(1.-1./(1.+((0.7*P1+0.3*P0)/Param(1)/E1)**2.)**0.5)
    !     ! fin speed-up

    ! Variables storage
    MISC(1) = E1            ! PE     ! [numeric] observed potential evapotranspiration [mm/year]
    MISC(2) = P1            ! Precip ! [numeric] observed total precipitation [mm/year]
    MISC(3) = Q             ! Qsim   ! [numeric] simulated outflow at catchment outlet [mm/year]

ENDSUBROUTINE

