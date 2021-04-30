build:
	@docker build -t vlan-controller:latest .

run: 
	@docker run -p 9000:8000 vlan-controller

