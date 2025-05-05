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
IMAGE_FORMAT="qcow2"
ADMIN_USER="admin"
ROLE_NAME="admin" # Change if you want to use a different role for the admin user in the project

FLAVOR_NAME="p2.tiny"
FLAVOR_CPU=1
FLAVOR_RAM=1024 # In MB
FLAVOR_DISK=5   # In GB


# Source the OpenStack credentials
source ~/admin-openrc.sh

# Create a project named "perry" with 100 CPU and 100GB RAM quota
openstack project create --description "Project Perry" "$PROJECT_NAME"
PROJECT_ID=$(openstack project show "$PROJECT_NAME" -f value -c id)
openstack quota set --cores $CPU_QUOTA --ram $RAM_QUOTA --instances $INSTANCE_QUOTA "$PROJECT_ID"
echo "Created project '$PROJECT_NAME' with CPU quota of $CPU_QUOTA and RAM quota of $RAM_QUOTA MB."

# Add the "admin" user to the "perry" project with the "admin" role
openstack role add --project "$PROJECT_NAME" --user "$ADMIN_USER" "$ROLE_NAME"
echo "Added user '$ADMIN_USER' to project '$PROJECT_NAME' with role '$ROLE_NAME'."

# Rename the "public" network to "external"
openstack network set --name "$NEW_NETWORK_NAME" "$NETWORK_NAME"
echo "Renamed network '$NETWORK_NAME' to '$NEW_NETWORK_NAME'."

# Add SSH key "perry_key" from a file
openstack keypair create --public-key "$KEY_FILE" "$KEY_NAME"
echo "Added SSH key '$KEY_NAME' from file '$KEY_FILE'."

# Upload an image and make it public
# openstack image create "$IMAGE_NAME" --file "$IMAGE_FILE" --disk-format "$IMAGE_FORMAT" --public
# echo "Uploaded image '$IMAGE_NAME' from '$IMAGE_FILE' and made it public."

# Create p1.tiny flavor
openstack flavor create "$FLAVOR_NAME" --vcpus "$FLAVOR_CPU" --ram "$FLAVOR_RAM" --disk "$FLAVOR_DISK"
echo "Created flavor '$FLAVOR_NAME' with $FLAVOR_CPU CPU, $FLAVOR_RAM MB RAM, and $FLAVOR_DISK GB disk."
