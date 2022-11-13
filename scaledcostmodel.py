# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 13:23:26 2022

@author: Fathaah
"""

import numpy as np
import matplotlib.pyplot as plt

# Output Arrays
production_units = np.arange(10,1501,1)
total_cost = np.zeros(np.size(production_units))

# Functional specification | Unit

V_cell = 2.2673 # Cell Voltage | V
j = 1/(0.0001) # Current Density | A/m2

P_cell = V_cell*j # Power Density | W/m2

A_cell_total = 781.61*(0.0001) # Total Cell Area | m2
A_cell_active = 781.61*0.91*(0.0001) # Active Cell Area | m2

P_stack = 1*(10**6) # Rated Stack Power | W

cell_num = np.ceil(P_stack/(P_cell*A_cell_active))

A_stack = cell_num*A_cell_total

A_stack_per_kW = A_stack/(P_stack*10**-3) # m2/kW

catalyst_loading = 25 #g/m2 | reference: plevova2022 (10.1016/j.jpowsour.2022.231476)

print("--------------------------------------------------------------")
print("Functional Specification of Electrolyzer Cell \n")

print("Cell Voltage: {:.2f} V".format(V_cell))
print("Current Density: {:.2f} A/cm2".format(j*0.0001))
print("Active Cell Area: {:.2f} cm2".format(A_cell_active/0.0001))
print("Rated Stack Power: {:.2f} W".format(P_stack))

print("Number of Cells: {:.0f}".format(cell_num))
print("Cell Area in 1 MW Stack: {:.2f} cm2".format(A_stack/0.0001))
print("--------------------------------------------------------------")

# Cost Breakdown

# Material costs 
cost_membrane_min = 159.81 # EUR/m2
cost_membrane_max = cost_membrane_min*2 # EUR/m2

# Membrane cost variation | format: [production size,cost,slope factor(for linear reduction)]
cost_membrane_variation_set = np.array([[10,cost_membrane_max,-0.710266667],[100,0.8*cost_membrane_max,-0.050507852],[1000,0.822222222*0.8*cost_membrane_max,-0.002579389],[20000,0.822222222*0.8*0.7668918920*cost_membrane_max,0]])

cost_ionomer = 2.90*10**3 # EUR/kg
cost_catalyst_NiCo2O4 = 1109.75*2 # EUR/kg
cost_catalyst_NiFe2O4 = 731.91*2 # EUR/kg

# Labor costs
cost_labor = 29.1 # EUR/hr/worker | source: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Hourly_labour_costs 

# Capital cost
cost_capital_max = 1000000*(1.252/1.0554) # EUR/machine | (1.252/1.0554) adjusts value for inflation from 2015 to 2022, and currency exchange
max_production_capacity = 50*109*60*16*0.0001*250*0.9 #m2/year | line speed 50cm/min, web width 109cm, 60min/hr, 16hrs/day, 250 days/year

# Energy cost
energy_max = 227 # KWh/m2 as per 10 unit production, back calculated from mayyas2019
energy_min = energy_max/production_units[-1]
avg_cost_energy = 9.97 # EUR/kWh | source: https://www.statista.com/statistics/1046605/industry-electricity-prices-european-union-country/

cost_energy_max = avg_cost_energy*energy_max #EUR/m2 | divide by number of units
cost_energy_min = avg_cost_energy*energy_min #EUR/m2 | divide by number of units

# Maintenance cost
cost_maintenance_max = 22.5*(A_stack*10)*(1.252/1.0554) # EUR | Divide this by the m2 to get EUR/m2

# Building cost
floor_space_cost = 81.63 # Average cost | EUR/m2
plant_footprint = 88.2 # m2

cost_building_max = floor_space_cost*plant_footprint # EUR | Divide this by the m2 to get EUR/m2

# Final cost calculation

total_cost_membrane = np.zeros(np.size(production_units))
i = 0; j = 0
for i in range(0,np.size(production_units)):
    while j < np.size(cost_membrane_variation_set)/3:
        if production_units[i] == cost_membrane_variation_set[j,0]:
            total_cost_membrane[i] = cost_membrane_variation_set[j,1]
            break
        elif production_units[i] > cost_membrane_variation_set[j,0] and production_units[i] < cost_membrane_variation_set[j+1,0]:
            total_cost_membrane[i] = cost_membrane_variation_set[j,2]*production_units[i] + (cost_membrane_variation_set[j,1]-cost_membrane_variation_set[j,2]*cost_membrane_variation_set[j,0])
            break
        else:
            j+=1


total_cost_catalyst = ((catalyst_loading*10**-3)*(cost_catalyst_NiCo2O4+cost_catalyst_NiFe2O4) + (2*catalyst_loading*10**-3)*(7/93)*cost_ionomer) * np.ones(np.size(production_units)) # EUR/m2

total_cost_capital = np.zeros(np.size(production_units))
i = 0; n = 1
for i in range(0,np.size(production_units)):
    if production_units[i]*A_stack <= max_production_capacity:
        total_cost_labor = (2*cost_labor*16*250)/(production_units*A_stack)
        total_cost_capital[i] = (cost_capital_max/15)/(production_units[i]*A_stack)
        total_cost_building = cost_building_max/(production_units*A_stack)
    else:
        while n < np.ceil(production_units[-1]*A_stack/max_production_capacity):
            if production_units[i]*A_stack > n*max_production_capacity and production_units[i]*A_stack <= (n+1)*max_production_capacity:
                total_cost_labor = (2*n*cost_labor*16*250)/(production_units*A_stack)
                total_cost_capital[i] = (cost_capital_max*n/15)/(production_units[i]*A_stack)
                total_cost_building = cost_building_max*n/(production_units*A_stack)
                break
            else:
                n+=1

total_cost_energy = cost_energy_max/production_units

total_cost_maintenance = cost_maintenance_max/(production_units*A_stack)

total_cost = total_cost_membrane + total_cost_catalyst + total_cost_labor + total_cost_capital + total_cost_energy + total_cost_maintenance + total_cost_building


# Total Cost Plot

fig_1, ax_1 = plt.subplots()
ax_1.plot(production_units, total_cost, linewidth=2.0)
ax_1.set(xlim=(production_units[0], production_units[-1]))
plt.title("Total Production Cost")
plt.xlabel("Production Size (Units/Year)")
plt.ylabel("Cost of Production (EUR/m2)")
plt.grid()
plt.show()

labels = ["Membrane","Catalyst & Ionomer","Direct Labor","Capital","Energy","Building","Maintenance"]

fig, ax = plt.subplots()
ax.stackplot(production_units, total_cost_membrane, total_cost_catalyst, total_cost_labor, total_cost_capital, total_cost_energy, total_cost_building, total_cost_maintenance, labels=labels)
ax.legend(loc='upper right')
plt.xlim([10,1500])
plt.title("Catalyst-Coated Membrane Production Cost (per m2)")
plt.xlabel("Production Size (Units/Year)")
plt.ylabel("Cost of Production (EUR/m2)")
plt.grid()
plt.show()

labels = ["Membrane","Catalyst & Ionomer","Direct Labor","Capital","Energy","Building","Maintenance"]

fig, ax = plt.subplots()
ax.stackplot(production_units, total_cost_membrane*A_stack_per_kW, total_cost_catalyst*A_stack_per_kW, total_cost_labor*A_stack_per_kW, total_cost_capital*A_stack_per_kW, total_cost_energy*A_stack_per_kW, total_cost_building*A_stack_per_kW, total_cost_maintenance*A_stack_per_kW, labels=labels)
ax.legend(loc='upper right')
plt.xlim([10,1500])
plt.title("Catalyst-Coated Membrane Production Cost (per kW)")
plt.xlabel("Production Size (Units/Year)")
plt.ylabel("Cost of Production (EUR/kW)")
plt.grid()
plt.show()



