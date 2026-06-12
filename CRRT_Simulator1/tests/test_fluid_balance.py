from models.fluid_balance import FluidBalance

fluid = FluidBalance()

fluid.add_intake(1000)
fluid.add_intake(500)

fluid.add_output(700)

print(fluid.get_data())