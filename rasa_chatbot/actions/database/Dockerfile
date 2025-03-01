FROM postgres:13

# Copy the backup data into the container
COPY pg_data_backup.tar.gz /tmp/pg_data_backup.tar.gz

# Extract the backup
RUN mkdir -p /var/lib/postgresql/data && \
    tar -xzf /tmp/pg_data_backup.tar.gz -C /var/lib/postgresql/data && \
    rm /tmp/pg_data_backup.tar.gz

# Set permissions for PostgreSQL to access the data
RUN chown -R postgres:postgres /var/lib/postgresql/data

# Expose the port
EXPOSE 5432

# Start PostgreSQL
CMD ["postgres"]