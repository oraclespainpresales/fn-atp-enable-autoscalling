import io
import json
import logging

import oci
from fdk import response

"""
This Function receives the Oracle Notification json and enable ATP autoscalling.
"""

def handler(ctx, data: io.BytesIO = None):
    try:
        jsonAlert = json.loads(data.getvalue())     
        alarmType = jsonAlert.get("type")
        if (alarmType == "OK_TO_FIRING"):
            dimensions = jsonAlert.get("alarmMetaData")[0].get("dimensions")
            resourceID = str(dimensions[0].get("resourceId"))
            logging.getLogger().info('JSON-resourceID: ' + resourceID.lower())
            updateADBScaling = updateADB(resourceID)
            #logging.getLogger().info('JSON-adb_data: ' + str(getADBDescription(resourceID)))
        else:
            updateADBScaling = '"message":"Do nothing when ' + alarmType + '"'
        
    except (ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))
        updateADBScaling = str(ex)
    except (Exception) as ex:
        logging.getLogger().info('error changing autoscaling: ' + str(ex))
        updateADBScaling = str(ex)

    return response.Response(
        ctx, response_data=json.dumps(updateADBScaling), headers={"Content-Type": "application/json"}
    )

def getADBDescription(resourceID):
    signer = oci.auth.signers.get_resource_principals_signer()
    adbClient = oci.database.DatabaseClient(config={},signer=signer)
    adb = adbClient.get_autonomous_database(resourceID.lower())
    return adb.data

def updateADB(resourceID):
    signer = oci.auth.signers.get_resource_principals_signer()
    adbClient = oci.database.DatabaseClient(config={},signer=signer)
    adb = adbClient.update_autonomous_database (
        autonomous_database_id=resourceID.lower(), 
        update_autonomous_database_details=oci.database.models.UpdateAutonomousDatabaseDetails(
            is_auto_scaling_enabled=True
        )
    )
        
    return adb.data
