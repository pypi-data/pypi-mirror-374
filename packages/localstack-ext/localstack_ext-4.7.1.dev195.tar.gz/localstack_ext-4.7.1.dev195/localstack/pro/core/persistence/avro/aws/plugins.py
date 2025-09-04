from localstack.runtime import hooks
@hooks.on_pro_infra_start()
def register_aws_avro_plugins():import py_avro_schema as A;from localstack.pro.core.persistence.avro.aws import base_store as B;A.register_schema(B.BaseStoreSchema)