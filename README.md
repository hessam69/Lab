# dc1 lab

1. Put these files in a repo, open in GitHub Codespaces (Open in Codespaces) or any Docker host.
2. `make up`  deploys the topology (FRR configs are mounted at boot).
3. `make test`  checks BGP EVPN sessions.
4. Change data, then `make configure` re-renders the Jinja template with Ansible.
