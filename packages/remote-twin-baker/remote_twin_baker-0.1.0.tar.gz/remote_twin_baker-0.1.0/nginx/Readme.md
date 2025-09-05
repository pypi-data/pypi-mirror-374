### 公网服务需配置https/SSL等转发规则 
## Developer Tasks
- **Nginx Setup**: Configure SSL certificates and DNS for `xxx.com`. Ensure HTTPS requests to `/twin_baker` proxy to `localhost:7777`.
- **Environment Sync**: Run `utils/merge_env_requirements.py` to align client and server environments. Fix any remaining mismatches manually based on test reports.
- **Server Deployment**: Deploy `app/server.py` on the remote host, ensuring port 7777 is accessible.
- **Configuration**: Update `config.yaml` with the production URL (`https://xxx.com/twin_baker`).