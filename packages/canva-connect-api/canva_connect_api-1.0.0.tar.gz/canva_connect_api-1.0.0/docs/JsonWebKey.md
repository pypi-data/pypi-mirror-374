# JsonWebKey

Standard Json Web Key specification following https://www.rfc-editor.org/rfc/rfc7517 and https://www.rfc-editor.org/rfc/rfc7518.html.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alg** | **str** | The \&quot;alg\&quot; (algorithm) parameter identifies the algorithm intended for use with the key. See https://www.rfc-editor.org/rfc/rfc7517#section-4 | [optional] 
**kid** | **str** | The \&quot;kid\&quot; (key ID) parameter is used to match a specific key.  This is used, for instance, to choose among a set of keys within a JWK Set during key rollover. When \&quot;kid\&quot; values are used within a JWK Set, different keys within the JWK Set SHOULD use distinct \&quot;kid\&quot; values. The \&quot;kid\&quot; value is a case-sensitive string. See https://www.rfc-editor.org/rfc/rfc7517#section-4 | 
**kty** | **str** | The \&quot;kty\&quot; (key type) parameter identifies the cryptographic algorithm family used with the key, such as \&quot;RSA\&quot; or \&quot;EC\&quot;. The \&quot;kty\&quot; value is a case-sensitive string. At the moment, only \&quot;RSA\&quot; is supported. See https://www.rfc-editor.org/rfc/rfc7517#section-4 | 
**n** | **str** | The \&quot;n\&quot; (modulus) parameter contains the modulus value for the RSA    public key.  It is represented as a Base64urlUInt-encoded value. See https://www.rfc-editor.org/rfc/rfc7518.html#section-6.3 | 
**e** | **str** | The \&quot;e\&quot; (exponent) parameter contains the exponent value for the RSA    public key.  It is represented as a Base64urlUInt-encoded value. See https://www.rfc-editor.org/rfc/rfc7518.html#section-6.3 | 
**use** | **str** | The \&quot;use\&quot; (public key use) parameter identifies the intended use of the public key. The \&quot;use\&quot; parameter is employed to indicate whether a public key is used for encrypting data or verifying the signature on data. Values are commonly \&quot;sig\&quot; (signature) or \&quot;enc\&quot; (encryption). See https://www.rfc-editor.org/rfc/rfc7517#section-4 | [optional] 

## Example

```python
from openapi_client.models.json_web_key import JsonWebKey

# TODO update the JSON string below
json = "{}"
# create an instance of JsonWebKey from a JSON string
json_web_key_instance = JsonWebKey.from_json(json)
# print the JSON string representation of the object
print(JsonWebKey.to_json())

# convert the object into a dict
json_web_key_dict = json_web_key_instance.to_dict()
# create an instance of JsonWebKey from a dict
json_web_key_from_dict = JsonWebKey.from_dict(json_web_key_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


