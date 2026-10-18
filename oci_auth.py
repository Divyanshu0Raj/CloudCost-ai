
# # import oci

# # # Load credentials from the OCI configuration file
# # config = oci.config.from_file(
# #     file_location=".oci/config",
# #     profile_name="DEFAULT",
# # )

# # # Validate the credentials locally
# # oci.config.validate_config(config)

# # print("OCI configuration loaded successfully.")
# # print("Region:", config["region"])

# import oci

# config = oci.config.from_file(
#     file_location=".oci/config",
#     profile_name="DEFAULT",
# )

# object_storage = oci.object_storage.ObjectStorageClient(config)
# namespace = object_storage.get_namespace().data

# # List buckets in the root compartment
# response = object_storage.list_buckets(
#     namespace_name=namespace,
#     compartment_id=config["tenancy"],
# )

# print("\n--- Available Buckets ---")

# for bucket in response.data:
#     print(bucket.name)

import oci

config = oci.config.from_file(
    file_location=".oci/config",
    profile_name="DEFAULT",
)

client = oci.object_storage.ObjectStorageClient(config)
namespace = client.get_namespace().data

# Inspect the two buckets found in your account
for bucket_name in ["cloudcost", "bucket-20260925-2007"]:
    print(f"\n--- Objects in {bucket_name} ---")

    try:
        response = client.list_objects(
            namespace_name=namespace,
            bucket_name=bucket_name,
        )

        objects = response.data.objects

        if not objects:
            print("No objects found.")

        for obj in objects:
            print(f"{obj.name} ({obj.size} bytes)")

    except oci.exceptions.ServiceError as error:
        print(f"OCI error: {error.status} - {error.message}")
