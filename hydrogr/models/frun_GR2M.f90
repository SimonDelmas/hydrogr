SUBROUTINE frun_GR2M(LInputs, InputsPrecip, InputsPE, NParam, Param, NStates, StateStart, NOutputs, IndOutputs, Outputs, StateEnd)
!
!    LInputs      , ! [integer] length of input and output series&
!    InputsPrecip , ! [double]  input series of total precipitation [mm/month]&
!    InputsPE     , ! [double]  input series of potential evapotranspiration (PE) [mm/month]&
!    NParam       , ! [integer] number of model parameters&
!    Param        , ! [double]  parameter set&
!    NStates      , ! [integer] number of state variables&
!    StateStart   , ! [double]  state variables used when the model run starts (store levels [mm])&
!    NOutputs     , ! [integer] number of output series&
!    IndOutputs   , ! [integer] indices of output series&
!    Outputs      , ! [double]  output series&
!    StateEnd       ! [double]  state variables at the end of the model run (store levels [mm])


    !     !DEC$ ATTRIBUTES DLLEXPORT :: frun_GR2M

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
    parameter (NMISC = 30)
    doubleprecision St(2)
    doubleprecision MISC(NMISC)
    doubleprecision P, E, Q
    integer I, K

    !     !--------------------------------------------------------------
    !     !Initializations
    !     !--------------------------------------------------------------

    !     !initialization of model states to zero
    St = 0.

    !     !initilisation of model states using StateStart
    St(1) = StateStart(1)
    St(2) = StateStart(2)

    !     !parameter values
    !     !Param(1) : production store capacity [mm]
    !     !Param(2) : groundwater exchange coefficient [-]

    !     !initialization of model outputs
    Q = -999.999
    MISC = -999.999
    !      StateEnd = -999.999 !initialization made in R
    !      Outputs = -999.999  !initialization made in R



    !     !--------------------------------------------------------------
    !     !Time loop
    !     !--------------------------------------------------------------
    DO k = 1, LInputs
        P = InputsPrecip(k)
        E = InputsPE(k)
        !        Q = -999.999
        !        MISC = -999.999
        !       !model run on one time step
        CALL MOD_GR2M(St, Param, P, E, Q, MISC)
        !       !storage of outputs
        DO I = 1, NOutputs
            Outputs(k, I) = MISC(IndOutputs(I))
        ENDDO
    ENDDO
    !     !model states at the end of the run
    StateEnd(1) = St(1)
    StateEnd(2) = St(2)

    RETURN

ENDSUBROUTINE


!################################################################################################################################




!**********************************************************************
SUBROUTINE MOD_GR2M(St, Param, P, E, Q, MISC)
    ! Calculation of streamflow on a single time step (month) with the GR2M model
    ! Inputs:
    !       St     Vector of model states at the beginning of the time step [mm]
    !       Param  Vector of model parameters (Param(1) [mm]; Param(2) [-])
    !       P      Value of rainfall during the time step [mm/month]
    !       E      Value of potential evapotranspiration during the time step [mm/month]
    ! Outputs:
    !       St     Vector of model states at the end of the time step [mm]
    !       Q      Value of simulated flow at the catchment outlet for the time step [mm/month]
    !       MISC   Vector of model outputs for the time step [mm]
    !**********************************************************************
    Implicit None
    INTEGER NMISC, NParam
    PARAMETER (NMISC = 30)
    PARAMETER (NParam = 2)
    DOUBLEPRECISION St(2)
    DOUBLEPRECISION Param(NParam)
    DOUBLEPRECISION MISC(NMISC)
    DOUBLEPRECISION P, E, Q
    DOUBLEPRECISION WS, tanHyp, S1, S2
    DOUBLEPRECISION P1, P2, P3, R1, R2, AE, EXCH

    DOUBLEPRECISION TWS, Sr, Rr ! speed-up

    ! Production store
    WS = P / Param(1)
    IF(WS.GT.13.)WS = 13.

    !	  ! speed-up
    TWS = tanHyp(WS)
    S1 = (St(1) + Param(1) * TWS) / (1. + St(1) / Param(1) * TWS)
    !  ! S1=(X(1)+Param(1)*tanHyp(WS))/(1.+X(1)/Param(1)*tanHyp(WS))
    ! 	  ! fin speed-up

    P1 = P + St(1) - S1
    WS = E / Param(1)
    IF(WS.GT.13.)WS = 13.

    !	  ! speed-up
    TWS = tanHyp(WS)
    S2 = S1 * (1. - TWS) / (1. + (1. - S1 / Param(1)) * TWS)
    !     ! S2=S1*(1.-tanHyp(WS))/(1.+(1.-S1/Param(1))*tanHyp(WS))
    !	  ! fin speed-up
    AE = S1 - S2

    ! Percolation
    !	  ! speed-up
    Sr = S2 / Param(1)
    Sr = Sr * Sr * Sr + 1.
    St(1) = S2 / Sr**(1. / 3.)
    !     ! X(1)=S2/(1+(S2/Param(1))**3.)**(1./3.)
    !	  ! fin speed-up

    P2 = S2 - St(1)
    P3 = P1 + P2

    ! QR calculation (routing store)
    R1 = St(2) + P3

    ! Water exchange
    R2 = Param(2) * R1
    EXCH = R2 - R1

    ! Total runoff
    Q = R2 * R2 / (R2 + 60.)

    ! Updating store level
    St(2) = R2 - Q


    ! Variables storage
    MISC(1) = E             ! PE     ! [numeric] observed potential evapotranspiration [mm/month]
    MISC(2) = P1            ! Precip ! [numeric] observed total precipitation  [mm/month]
    MISC(3) = AE            ! AE     ! [numeric] actual evapotranspiration [mm/month]
    MISC(4) = P2            ! P2     ! [numeric] percolation (P2) [mm/month]
    MISC(5) = P3            ! P3     ! [numeric] P3=P1+P2 [mm/month]
    MISC(6) = EXCH          ! EXCH   ! [numeric] groundwater exchange (EXCH) [mm/month]
    MISC(7) = St(1)         ! Prod   ! [numeric] production store level (St(1)) [mm]
    MISC(8) = St(2)         ! Rout   ! [numeric] routing store level (St(2)) [mm]
    MISC(9) = Q             ! Qsim   ! [numeric] simulated outflow at catchment outlet [mm/month]

ENDSUBROUTINE

