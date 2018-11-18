class uServerRoutes:
    def __init__(self, route, method, func, routeArgNames, routeRegex):
        self.route = route
        self.method = method
        self.func = func
        self.routeArgNames = routeArgNames
        self.routeRegex = routeRegex
