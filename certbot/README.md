# Certbot Configuration Directory

This directory contains configuration files for Certbot, which is used to obtain and renew SSL/TLS certificates.

## Directory Structure

- `config/` - Contains configuration files
  - `cloudflare.ini` - Cloudflare API credentials for DNS-01 challenges (not checked into version control)
- `www/` - Web root for HTTP-01 challenges
  - `.well-known/acme-challenge/` - Directory where challenge files are placed

## Using DNS-01 Challenge with Cloudflare

For DNS-01 challenges, you need to create a `cloudflare.ini` file in the `config/` directory with the following content:

```ini
dns_cloudflare_api_token = your_cloudflare_api_token
```

This file should have permissions set to 600 (read/write for owner only) for security:

```bash
chmod 600 config/cloudflare.ini
```

See `README-DNS-CLOUDFLARE.md` in the project root for detailed instructions.

## Security Note

Never commit API tokens or credentials to version control. Files containing sensitive data should be added to `.gitignore`.