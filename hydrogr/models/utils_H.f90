!**********************************************************************
SUBROUTINE UH1_H(OrdUH1, C, D)
    ! Computation of ordinates of GR unit hydrograph UH2 using successive differences on the S curve SS1
    ! Inputs:
    !    C: time constant
    !    D: exponent
    ! Outputs:
    !    OrdUH1: NH ordinates of discrete hydrograph
    !**********************************************************************
    Implicit None
    INTEGER NH
    PARAMETER (NH = 480)
    DOUBLEPRECISION OrdUH1(NH)
    DOUBLEPRECISION C, D, SS1_H
    INTEGER I

    DO I = 1, NH
        OrdUH1(I) = SS1_H(I, C, D) - SS1_H(I - 1, C, D)
    ENDDO
ENDSUBROUTINE


!**********************************************************************
SUBROUTINE UH2_H(OrdUH2, C, D)
    ! Computation of ordinates of GR unit hydrograph UH2 using successive differences on the S curve SS2
    ! Inputs:
    !    C: time constant
    !    D: exponent
    ! Outputs:
    !    OrdUH2: 2*NH ordinates of discrete hydrograph
    !**********************************************************************
    Implicit None
    INTEGER NH
    PARAMETER (NH = 480)
    DOUBLEPRECISION OrdUH2(2 * NH)
    DOUBLEPRECISION C, D, SS2_H
    INTEGER I

    DO I = 1, 2 * NH
        OrdUH2(I) = SS2_H(I, C, D) - SS2_H(I - 1, C, D)
    ENDDO
ENDSUBROUTINE


!**********************************************************************
FUNCTION SS1_H(I, C, D)
    ! Values of the S curve (cumulative HU curve) of GR unit hydrograph HU1
    ! Inputs:
    !    C: time constant
    !    D: exponent
    !    I: time-step
    ! Outputs:
    !    SS1: Values of the S curve for I
    !**********************************************************************
    Implicit None
    DOUBLEPRECISION C, D, SS1_H
    INTEGER I, FI

    FI = I
    IF(FI.LE.0) THEN
        SS1_H = 0.
        RETURN
    ENDIF
    IF(FI.LT.C) THEN
        SS1_H = (FI / C)**D
        RETURN
    ENDIF
    SS1_H = 1.
ENDFUNCTION


!**********************************************************************
FUNCTION SS2_H(I, C, D)
    ! Values of the S curve (cumulative HU curve) of GR unit hydrograph HU2
    ! Inputs:
    !    C: time constant
    !    D: exponent
    !    I: time-step
    ! Outputs:
    !    SS2: Values of the S curve for I
    !**********************************************************************
    Implicit None
    DOUBLEPRECISION C, D, SS2_H
    INTEGER I, FI

    FI = I
    IF(FI.LE.0) THEN
        SS2_H = 0.
        RETURN
    ENDIF
    IF(FI.LE.C) THEN
        SS2_H = 0.5 * (FI / C)**D
        RETURN
    ENDIF
    IF(FI.LT.2. * C) THEN
        SS2_H = 1. - 0.5 * (2. - FI / C)**D
        RETURN
    ENDIF
    SS2_H = 1.
ENDFUNCTION
