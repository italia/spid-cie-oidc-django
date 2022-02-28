# How to export the OP's metadata schema for SPID

````
./manage.py shell
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataSpid
print(OPMetadataSpid.schema_json(indent=2))
````

# How to validate the OP's metadata for SPID

````
./manage.py shell
````
Import an OP's metadata example
````
from spid_cie_oidc.provider.tests.op_metadata_settings import OP_METADATA_SPID
````
Then to validate
````
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataSpid
OPMetadataSpid(**OP_METADATA_SPID)
````


# How to export the OP's metadata schema for CIE

````
./manage.py shell
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataCie
print(OPMetadataCie.schema_json(indent=2))
````

# How to validate the OP's metadata for SPID

````
./manage.py shell
````
Import an OP's metadata example
````
from spid_cie_oidc.provider.tests.op_metadata_settings import OP_METADATA_CIE
````
Then to validate
````
from spid_cie_oidc.provider.schemas.op_metadata import OPMetadataCie
OPMetadataCie(**OP_METADATA_CIE)