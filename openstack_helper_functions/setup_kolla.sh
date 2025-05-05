#!/bin/bash
set -e

# Set variables
PROJECT_NAME="perry"
INSTANCE_QUOTA=100
CPU_QUOTA=100
RAM_QUOTA=102400 # In MB

NETWORK_NAME="public"
NEW_NETWORK_NAME="external"
KEY_NAME="perry_key"
KEY_FILE="~/perry_key.pub"
IMAGE_NAME="Ubuntu20"
IMAGE_FILE="~/Ubuntu20.raw"
KALI_IMAGE_NAME="Kali"
KALI_IMAGE_FILE="~/kali.qcow2"
IMAGE_FORMAT="qcow2"
ADMIN_USER="admin"
ROLE_NAME="admin" # Change if you want to use a different role for the admin user in the project

# Source the OpenStack credentials
source /etc/kolla/admin-openrc.sh

# External network
EXTERNAL_NETWORK_NAME="external"        # Name of the external network
SUBNET_NAME="ext-subnet"              # Name of the subnet
CIDR="192.168.0.0/24 "               # CIDR for the subnet
DNS_SERVER="8.8.8.8"                  # DNS server
PHYSICAL_NETWORK="physnet1"

openstack network create --external $EXTERNAL_NETWORK_NAME
openstack subnet create \
  --network "$EXTERNAL_NETWORK_NAME" \
  --subnet-range "$CIDR" \
  --gateway "$GATEWAY" \
  --dns-nameserver "$DNS_SERVER" \
  --provider-network-type flat \
  --provider-physical-network $PHYSICAL_NETWORK \
  --no-dhcp \
  "$SUBNET_NAME"

# # Create a project named "perry" with 100 CPU and 100GB RAM quota
# openstack project create --description "Project Perry" "$PROJECT_NAME"
# PROJECT_ID=$(openstack project show "$PROJECT_NAME" -f value -c id)
# openstack quota set --cores $CPU_QUOTA --ram $RAM_QUOTA --instances $INSTANCE_QUOTA "$PROJECT_ID"
# echo "Created project '$PROJECT_NAME' with CPU quota of $CPU_QUOTA and RAM quota of $RAM_QUOTA MB."

# # Add the "admin" user to the "perry" project with the "admin" role
# openstack role add --project "$PROJECT_NAME" --user "$ADMIN_USER" "$ROLE_NAME"
# echo "Added user '$ADMIN_USER' to project '$PROJECT_NAME' with role '$ROLE_NAME'."

# # Add SSH key "perry_key" from a file
# openstack keypair create --public-key "$KEY_FILE" "$KEY_NAME"
# echo "Added SSH key '$KEY_NAME' from file '$KEY_FILE'."

# # Create p1.tiny flavor
# FLAVOR_NAME="p2.tiny"
# FLAVOR_CPU=1
# FLAVOR_RAM=1024 # In MB
# FLAVOR_DISK=5   # In GB
# openstack flavor create "$FLAVOR_NAME" --vcpus "$FLAVOR_CPU" --ram "$FLAVOR_RAM" --disk "$FLAVOR_DISK"
# echo "Created flavor '$FLAVOR_NAME' with $FLAVOR_CPU CPU, $FLAVOR_RAM MB RAM, and $FLAVOR_DISK GB disk."

# # m1.small flavor
# FLAVOR_NAME="m1.small"
# FLAVOR_CPU=1
# FLAVOR_RAM=2048 # In MB
# FLAVOR_DISK=20  # In GB
# openstack flavor create "$FLAVOR_NAME" --vcpus "$FLAVOR_CPU" --ram "$FLAVOR_RAM" --disk "$FLAVOR_DISK"
# echo "Created flavor '$FLAVOR_NAME' with $FLAVOR_CPU CPU, $FLAVOR_RAM MB RAM, and $FLAVOR_DISK GB disk."

# # Upload an image and make it public
# openstack image create "$IMAGE_NAME" --file "$IMAGE_FILE" --disk-format "$IMAGE_FORMAT" --public
# echo "Uploaded image '$IMAGE_NAME' from '$IMAGE_FILE' and made it public."

# # Upload an image and make it public
# openstack image create "$KALI_IMAGE_NAME" --file "$KALI_IMAGE_FILE" --disk-format "$KALI_IMAGE_FORMAT" --public
# echo "Uploaded image '$KALI_IMAGE_NAME' from '$KALI_IMAGE_FILE' and made it public."
