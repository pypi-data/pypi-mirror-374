# ExportErrorCode

If the export failed, this specifies the reason why it failed.  - `license_required`: The design contains [premium elements](https://www.canva.com/help/premium-elements/) that haven't been purchased. You can either buy the elements or upgrade to a Canva plan (such as Canva Pro) that has premium features, then try again. Alternatively, you can set `export_quality` to `regular` to export your document in regular quality. - `approval_required`: The design requires [reviewer approval](https://www.canva.com/en_au/help/design-approval/) before it can be exported. - `internal_failure`: The service encountered an error when exporting your design.

## Enum

* `LICENSE_REQUIRED` (value: `'license_required'`)

* `APPROVAL_REQUIRED` (value: `'approval_required'`)

* `INTERNAL_FAILURE` (value: `'internal_failure'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


