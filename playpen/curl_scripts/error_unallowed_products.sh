
if [ $# -lt 1 ]; then
    export SAMPLE_RHIC=../../src/splice/test_data/valid_cert/sample_rhic_valid.pem
else
    export SAMPLE_RHIC=$1
fi
export SERVER_ADDR=`hostname`
export PORT=443
export CA_CERT=/etc/pki/splice/Splice_CA.cert
export CONSUMER_IDENTITY="98e6aa41-a25d-4d60-976b-d70518382683"
export DATA="{\"consumer_identifier\":\"F0:DE:F1:DE:88:2B\", \"products\": [\"23\", \"24\", \"26\"], \"system_facts\": {\"tbd\":\"values\"}}"

echo "Using RHIC from ${SAMPLE_RHIC}"
echo curl -s -S -E ${SAMPLE_RHIC} --cacert ${CA_CERT} --dump-header - -H "Content-Type: application/json" -X POST --data "${DATA}" https://${SERVER_ADDR}:${PORT}/splice/api/v1/entitlement/${CONSUMER_IDENTITY}/ 
curl -s -S -E ${SAMPLE_RHIC} --cacert ${CA_CERT} --dump-header - -H "Content-Type: application/json" -X POST --data "${DATA}" https://${SERVER_ADDR}:${PORT}/splice/api/v1/entitlement/${CONSUMER_IDENTITY}/ 

