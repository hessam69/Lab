fwimage:
	docker build -t fwlab:latest fw/
up: fwimage
	sudo containerlab deploy -t lab.clab.yml
down:
	sudo containerlab destroy -t lab.clab.yml --cleanup
test:
	@for n in clab-dc1-leaf1 clab-dc1-leaf2 clab-dc1-leaf3; do echo $$n; docker exec $$n vtysh -c 'show bgp l2vpn evpn summary'; done
fwtest:
	@docker exec clab-dc1-client1 ping -c 2 -W 2 10.20.1.10 || true
	@docker exec clab-dc1-client1 curl -s -m 3 -o /dev/null -w "port 443 -> %{http_code}\\n" http://10.20.1.10:443 || echo "port 443 -> blocked"
	@docker exec clab-dc1-client1 curl -s -m 3 -o /dev/null -w "port 80 -> %{http_code}\\n" http://10.20.1.10:80 || echo "port 80 -> blocked"
