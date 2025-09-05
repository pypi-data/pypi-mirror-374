# PowerShell Code Signing Management

This document provides guidance for managing code signing certificates for PowerShell scripts in the NetBox EntraID Tools project.

## Why Sign PowerShell Scripts?

Signing PowerShell scripts offers several benefits:

1. **Security**: Validates that the script comes from a trusted publisher and hasn't been tampered with
2. **Execution Policy Compatibility**: Allows execution on systems with restricted execution policies
3. **Professionalism**: Demonstrates commitment to secure deployment practices

## Signing Process

After modifying a PowerShell script, you should re-sign it using your code signing certificate:

```powershell
# Sign a single script
Set-AuthenticodeSignature -FilePath "C:\Scripts\netbox_entraid_tools-x.y.z\Bump-FolderVersion.ps1" -Certificate (Get-ChildItem Cert:\CurrentUser\My\<CertificateThumbprint>)

# Alternatively, sign all PowerShell scripts in the project
Get-ChildItem -Path "C:\Scripts\netbox_entraid_tools-x.y.z\*.ps1" -Recurse | ForEach-Object {
    Set-AuthenticodeSignature -FilePath $_.FullName -Certificate (Get-ChildItem Cert:\CurrentUser\My\<CertificateThumbprint>)
}
```

Replace `<CertificateThumbprint>` with your certificate's thumbprint.

## Certificate Management

### Finding Your Certificate

```powershell
# List available code signing certificates
Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
```

### Creating a Self-Signed Certificate (For Testing)

```powershell
# Create a self-signed certificate for development purposes
$cert = New-SelfSignedCertificate -Subject "CN=PowerShell Code Signing" -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My
```

### Verifying a Signature

```powershell
# Verify the signature on a script
Get-AuthenticodeSignature -FilePath "C:\Scripts\netbox_entraid_tools-x.y.z\Bump-FolderVersion.ps1"
```

## Best Practices

1. Always re-sign scripts after making changes
2. Include signature verification in your deployment process
3. Keep your signing certificate secure
4. Use timestamp servers when signing to ensure signatures remain valid after certificate expiration:

```powershell
Set-AuthenticodeSignature -FilePath "path\to\script.ps1" -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
```

## Automated Signing

Consider adding a post-build script that automatically signs all PowerShell scripts:

```powershell
# Example post-build signing script
$cert = Get-ChildItem Cert:\CurrentUser\My\<CertificateThumbprint>
$files = Get-ChildItem -Path ".\*.ps1" -Recurse
foreach ($file in $files) {
    Set-AuthenticodeSignature -FilePath $file.FullName -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
}
```
