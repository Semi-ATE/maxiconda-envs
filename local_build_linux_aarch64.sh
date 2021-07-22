chmod -R -c o+w ./*
export MAXICONDA_ARGS="--solve --build"
docker run --rm --privileged multiarch/qemu-user-static --reset --credential yes --persistent yes
docker run --rm -v "$(pwd):/maxiconda-envs" -e MAXICONDA_ARGS condaforge/linux-anvil-aarch64 /maxiconda-envs/scripts/linux-aarch64.sh
