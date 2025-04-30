# DNS Authentication with Cloudflare

This project now supports DNS-01 challenge authentication for SSL certificate generation, which allows you to generate certificates without exposing port 80 to the internet. This is especially useful for:

- Servers behind strict firewalls
- Obtaining wildcard certificates
- Services running in private networks

## Setup Instructions

### 1. Create a Cloudflare API Token

1. Log in to your Cloudflare account
2. Navigate to "My Profile" > "API Tokens"
3. Create a new token with the following permissions:
   - Zone > DNS > Edit
   - Zone > Zone > Read
4. Use Zone Resources > Include > Specific zone > Your domain(s)
5. Copy the generated token for the next step

### 2. Configure Your Environment

Add the following variables to your `.env` file:

```
CF_API_TOKEN=your_api_token_from_cloudflare
CF_ZONE_ID=your_zone_id_from_cloudflare
CF_EMAIL=your_email@example.com
BASE_DOMAIN=your-domain.com
SERVER_IP=your_server_ip
```

The Zone ID can be found in your Cloudflare dashboard under the domain's "Overview" tab.

### 3. Using DNS Challenge Authentication

DNS authentication is now the default method. When running the setup command, the tool will:

1. Create a temporary self-signed certificate
2. Create a Cloudflare credentials file
3. Use the DNS-01 challenge to obtain a proper certificate

```bash
proxy-manager setup --subdomain example --local-port 3000 --allowed-ip 10.0.0.1
```

### Falling Back to HTTP Challenge

If you prefer to use the HTTP-01 challenge method, you can use the `--use-http-challenge` flag:

```bash
proxy-manager setup --subdomain example --local-port 3000 --allowed-ip 10.0.0.1 --use-http-challenge
```

## Troubleshooting

If certificate issuance fails with DNS challenge:

1. Check that your Cloudflare API token has the correct permissions
2. Verify the domain is managed by the Cloudflare zone specified in CF_ZONE_ID
3. Check the certbot logs: `docker-compose logs certbot`
4. Try using the HTTP challenge as a fallback if DNS propagation is an issue

## Security Notes

- The Cloudflare credentials file is stored with 600 permissions (owner read/write only)
- API tokens are more secure than using the global API key
- The token should be restricted to only the necessary zones and permissions