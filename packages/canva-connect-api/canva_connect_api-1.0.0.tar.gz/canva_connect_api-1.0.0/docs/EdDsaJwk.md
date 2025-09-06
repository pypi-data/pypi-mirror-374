# EdDsaJwk

A JSON Web Key Set (JWKS) using the Edwards-curve Digital Signature Algorithm (EdDSA), as described in [RFC-8037](https://www.rfc-editor.org/rfc/rfc8037.html#appendix-A).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kid** | **str** | The &#x60;kid&#x60; (key ID) is a unique identifier for a public key. When the keys used to sign webhooks are rotated, you can use this ID to select the correct key within a JWK Set during the key rollover. The &#x60;kid&#x60; value is case-sensitive. | 
**kty** | **str** | The &#x60;kty&#x60; (key type) identifies the cryptographic algorithm family used with the key, such as \&quot;RSA\&quot; or \&quot;EC\&quot;. Only Octet Key Pairs (&#x60;OKPs&#x60;) are supported. The &#x60;kty&#x60; value is case-sensitive. For more information on the &#x60;kty&#x60; property and OKPs, see [RFC-8037 — \&quot;kty\&quot; (Key Type) Parameter](https://www.rfc-editor.org/rfc/rfc8037.html#section-2). | 
**crv** | **str** | The &#x60;crv&#x60; (curve) property identifies the curve used for elliptical curve encryptions. Only \&quot;Ed25519\&quot; is supported. For more information on the &#x60;crv&#x60; property, see [RFC-8037 — Key Type \&quot;OKP\&quot;](https://www.rfc-editor.org/rfc/rfc8037.html#section-2). | 
**x** | **str** | The &#x60;x&#x60; property is the public key of an elliptical curve encryption. The key is Base64urlUInt-encoded. For more information on the &#x60;x&#x60; property, see [RFC-8037 — \&quot;x\&quot; (X Coordinate) Parameter](https://www.rfc-editor.org/rfc/rfc8037#section-2). | 

## Example

```python
from openapi_client.models.ed_dsa_jwk import EdDsaJwk

# TODO update the JSON string below
json = "{}"
# create an instance of EdDsaJwk from a JSON string
ed_dsa_jwk_instance = EdDsaJwk.from_json(json)
# print the JSON string representation of the object
print(EdDsaJwk.to_json())

# convert the object into a dict
ed_dsa_jwk_dict = ed_dsa_jwk_instance.to_dict()
# create an instance of EdDsaJwk from a dict
ed_dsa_jwk_from_dict = EdDsaJwk.from_dict(ed_dsa_jwk_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


