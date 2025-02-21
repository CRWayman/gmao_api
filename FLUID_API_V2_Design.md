**FLUID API Version 2 Design**

Issues with version 1:

-   Endpoints not organized into separately defined modules
    -   Introduce static urls for parameters that have a fixed set of options (ex: collection, dataset)
-   A single view is handling multiple endpoints, multiple functionality
-   Path parameters not required for certain cases but still require input
-   Too many checks to handle individual cases for path parameters

Potential fixes in version 2:

-   Modules and submodules
    -   Separate concerns and responsibilities into different modules
    -   Example modules: fcast, assim
    -   Also helps structure and organize the API Docs generated from FastAPI
-   APIRouter
    -   <https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter>
    -   Resolves path operations inside a module
    -   Define a prefix that all path urls in this module share:
        -   Prefix= “/fcast”
        -   All views in this module can just use the relative path
    -   SSOT
-   Designate views that solely return a description about current endpoint in JSON
-   Designate views that solely return JSON data from data source (wxmaps)
-   Design philosophy: Focus on creating small, isolated functions with clear single responsibilities

Layout of Datasets:

-   Fcst
    -   Chm
        -   V1
            -   No2
            -   O3
            -   Pm2.5
            -   Hcho
            -   Co
            -   so2
        -   p23
            -   ""
    -   Met
        -   X1
            -   MET
        -   P23
            -   MET
-   Assim
    -   Aqc
        -   V1
            -   No2
            -   O3
            -   pm2.5
    -   Chm
        -   V1
        -   P23
        -   V72
    -   Met
        -   X1
        -   p23
        -   v72
