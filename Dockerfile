FROM python:3.12-slim-bookworm

# ENVs
ENV PYTHONWARNINGS="ignore"

# Install pip requirements
COPY requirements.txt /
RUN python -m pip install -r /requirements.txt

#C Copy app
COPY . /mcp-server-junos
RUN ls -al /mcp-server-junos/

# Run application
WORKDIR "/mcp-server-junos"
CMD ["python3", "mcp_server_junos.py"]