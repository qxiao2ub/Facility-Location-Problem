from gurobipy import *


def FacilityLocation(Arcs, Depot, Customer, demand, cost, capacity, shippingCost):

    model = Model()

    build = {} #Build depot decision
    serve = {} #from depot i serve customer j

    for i in Depot:
        build[i] = model.addVar(vtype=GRB.BINARY, obj = cost[i], name="x_%g"%i)

    for i,j in Arcs:
        serve[i,j] = model.addVar(vtype=GRB.CONTINUOUS, ub = 1, obj = shippingCost[i,j], name="f_%g_%g"%(i,j))

    model.update()
    model.modelSense = GRB.MINIMIZE

    #Satisfy each customer demand:

    for j in Customer:
        model.addConstr(quicksum(serve[i,j] for i,j in Arcs.select('*', j)) == 1, name="demand_%g"%j)

    # Do not exceed capacity
    # Cannot service a customer from an unbuilt depot

    for i in Depot:
        model.addConstr(quicksum(demand[j]*serve[i,j] for i,j in Arcs.select(i,'*')) <= capacity[i]*build[i], name="capacity_%g"%i)

    def printSolution():
        if model.status == GRB.status.OPTIMAL:
            print("\nOptimal Solution: %g" %model.objVal)
            print("Building Cost: %g"%(quicksum(cost[i]*build[i] for i in Depot).getValue()))
            print("Shipping Cost: %g"%(quicksum(shippingCost[i,j]*serve[i,j] for i,j in Arcs).getValue()))
            print("\nPlace Facilities at:")
            for i in Depot:
                if build[i].x > 0.1:
                    print("Build depot {}".format(i))
            for i,j in Arcs:
                if serve[i,j].x > 0.001:
                    print(str.format("Customer {} serviced {} units by depot {}", j,serve[i,j].x*demand[j],i))
        else:
            print('No solution')

    model.optimize()
    printSolution()
