This following example demonstrates the mesh metrics feature for a poor mesh of the unswept CRM wing.

To run the demo case perform one of the following steps:

If the mesh is already uploaded on the flexcompute servers, run `python submit_case_from_mesh_id.py` -> this script will upload the case with a poor surface mesh, which will trigger mesh metrics validation warnings. 

Alternatively, the mesh can be uploaded using `python submit_mesh_from_download.py`. The case can then be uploaded using `python submit_case_from_mesh_name` Note that the mesh metrics can take a short amount of time to be calculated, once the mesh is uploaded. To check whether the mesh metrics are available, the following script can be ran: `python download_mesh_metrics`.
