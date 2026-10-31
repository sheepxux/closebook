# Docker basics (onboarding notes)

1. **Image vs container.** An image is a read-only template built in layers; a container is a running (or stopped) instance of an image with its own writable layer. Deleting a container loses that writable layer.
2. **Common commands.** `docker build -t app:1.0 .` builds an image from a Dockerfile; `docker run -d -p 8080:80 app:1.0` starts a container in the background and maps host port 8080 to container port 80; `docker ps` lists running containers; `docker logs <id>` shows output; `docker exec -it <id> sh` opens a shell inside.
3. **Volumes vs bind mounts.** Named volumes are managed by Docker and are the default choice for database data; bind mounts map a host path and are handy for live-editing source code in development, but tie the container to the host's directory layout.
4. **Default ports to remember.** PostgreSQL 5432, MySQL 3306, Redis 6379, HTTP 80, HTTPS 443.
5. **Layer caching.** Put rarely changing steps (installing dependencies) before frequently changing ones (copying source) so rebuilds reuse cached layers.
