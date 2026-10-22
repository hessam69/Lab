up:
	sudo containerlab deploy -t lab.clab.yml
down:
	sudo containerlab destroy -t lab.clab.yml --cleanup
configure:
	ansible-playbook -i inventory.yml playbook.yml
test:
	@for n in clab-dc1-leaf1 clab-dc1-leaf2 clab-dc1-leaf3; do echo $$n; docker exec $$n vtysh -c 'show bgp l2vpn evpn summary'; done
