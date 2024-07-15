
class convertor:
    def I_to_E(I, area, conductivity):
        J = I / area
        E = J / conductivity # unit of E: V/m

        print("The E-field on the target should be larger than {} V/m".format(E))
        return E

    def E_to_I(highest_E, lowest_E, area, sigma):
        # E_field calculation
        E1 = (highest_E + lowest_E)/2
        E2 = highest_E - E1

        # I calculation
        # I1 + I2 = highest_E
        # I1 - I2 = lowest_E
        highest_I = sigma * highest_E * area
        lowest_I = sigma * lowest_E * area
        I1 = (highest_I + lowest_I)/2
        I2 = highest_I - I1

        print("The currents E1 and E2 are {}V and {}V".format(E1, E2))
        print("The currents I1 and I2 are {}nA and {}nA".format(I1*10**9, I2*10**9))
        
        return E1, E2, I1, I2