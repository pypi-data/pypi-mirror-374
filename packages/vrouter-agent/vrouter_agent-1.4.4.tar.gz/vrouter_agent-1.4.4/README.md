# vRouter-agent
[![Build and Sync Package to S3](https://github.com/Unified-Sentinel-Data-Networks/vrouter-agent/actions/workflows/publish-vrouter-agent-s3.yml/badge.svg)](https://github.com/Unified-Sentinel-Data-Networks/vrouter-agent/actions/workflows/publish-vrouter-agent-s3.yml)


# Overview 
vRouter-agent is a custom module built by USDN to handle and execute transaction from customer portal to each node. 


# Requirements

- [python][python] >= 3.10
- [vpp][vpp] >= v20.06
- [multichain][multichain] > v2.3.1
- [Fast API][fastapi] > v0.115
- [FRR][frr] > v8.3
- [vrouter][vrouter] > v1.0.6
- [poetry][poetry] > v1.6.1

# Development
This project is managed by poetry. Use poetry to install and run script.
 
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry install 
poetry run server
```

# Deployment 
### Run vrouter-agent as a service

vRouter depends on different services. In order to run vrouter-agent, these services must be up and running:
- VPP
- vRouter
- multichaind@{{chain}}. Chain is what defined in the nodecontrol 
- FRR

#### Create service file: 

```bash
sudo nano /etc/systemd/system/vrouter_agent.service
```

```bash
Requires=multichaind@{{chain}}
After=network.target multichaind@{{chain}} vpp.service vrouter.service

[Service]
Type=simple
ExecStartPre=/usr/local/bin/poetry/bin/poetry install 
ExecStart=/usr/local/bin/poetry/bin/poetry run server 
Restart=on-failure
RestartSec=30
WorkingDirectory=/opt/vrouter-agent/bin
User={{user}}
ExecStopPost=/bin/bash -c 'echo "$(date) $(hostname) vrouter agent service stopped" >> /var/log/vrouter-agent.log'
ExecRestartPost=/bin/bash -c 'echo "$(date) $(hostname) vrouter agent service restarted" >> /var/log/vrouter-agent.log'
OnFailure=/bin/bash -c 'echo "$(date) $(hostname) vrouter agent service failed" >> /var/log/vrouter-agent.log'

[Install]
WantedBy=multi-user.target

```

#### Enable service at boot and start service:

```bash
sudo systemctl enable vrouter-agent && sudo systemctl start vrouter-agent 
```

# Usage

### Run manually

```bash
cd /opt/vrouter-agent/bin
poetry install && poetry run server
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[US Data Networks](https://usdatanetworks/docs/license)

[python]: https://www.python.org/downloads/release/python-380/
[pip]: https://pip.pypa.io/en/stable/installation/
[vpp]: https://s3-docs.fd.io/vpp/22.06/
[multichain]: https://www.multichain.com/download-community/
[fastapi]: https://fastapi.tiangolo.com/
[frr]: https://gallery.ecr.aws/p6l6k3o9/frr
[vrouter]: https://github.com/Unified-Sentinel-Data-Networks/vrouter-pantheon
[poetry]: https://install.python-poetry.org