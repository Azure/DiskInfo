
# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

# Overview
This open source tool is used by Microsoft for collecting telemetry information from storage devices. It is intended to be used by independent hardware vendors (IHVs) to ensure tool compatibility with their devices and to relay the necessary information for Microsoft to collect pertinent vendor unique logs from IHV devices.

By using this tool, IHVs can verify the data being collected is accurate and does not disrupt device performance.

Note: It is understood vendor unique telemetry data can be protected IP, so vendor unique classifier, model, and log page extensions may not be upstreamed to this repository unless vendors choose to. Instead, a private branch can be created by the IHV and extensions shared with Microsoft for integration into Microsoft private branch.

# Quick Setup
The tool will automatically scan for physical storage devices on the execution system, output data to diskData.json file in the top level directory, and print information to screen by running the following command:

  # python runner.py
  
To output to a specific directory, a parameter can be provided like so:

  # python runner.py example/output/dir
  
# Vendor Specific Extensions
To add vendor specific telemetry data, the following changes must occur:
  1. Update src/classify.py to ensure the proper function is returned from vendor specific model file (e.g. Models.ExampleVendorFile.NVME) based on the Product ID, Bus Type, and Manufacturer info collected by WMIC. This should only need to be done once per model (i.e. not for each additional log page added).
  2. Update vendor specific model file (e.g. src/Models/ExampleVendorFile.py) to return a tuple of supported vendor unique log pages based on the function provided in step 1, the model number, and the firmware revision.
  3. Add JSON file to vendor specific log page folder (e.g. src/LogPages/ExampleVendor/VU1.json) to properly parse vendor unique log page.
