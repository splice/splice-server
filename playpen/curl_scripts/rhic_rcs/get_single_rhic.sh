source source_me
export SERVER_ADDR=`hostname`
echo curl --cacert ${CA_CERT} --cert ${CLIENT_CERT} --key ${CLIENT_KEY} -s -S --dump-header - -H "Content-Type: application/json" -X GET https://${SERVER_ADDR}/splice/api/v1/rhicrcs/7dd72d62-fcf2-4e5c-a659-273bb88bd509/
curl --cacert ${CA_CERT} --cert ${CLIENT_CERT} --key ${CLIENT_KEY} -s -S --dump-header - -H "Content-Type: application/json" -X GET https://${SERVER_ADDR}/splice/api/v1/rhicrcs/7dd72d62-fcf2-4e5c-a659-273bb88bd509/

