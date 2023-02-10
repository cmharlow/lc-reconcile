FROM continuumio/miniconda3

WORKDIR /reconcile

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "lc-reconcile", "/bin/bash", "-c"]

# Installed by default now
# RUN conda install -c conda-forge requests-cache

# The code to run when container is started:
COPY *.py .
# User must append an identification string when running ie docker run lc-reconcile "Your Name email@example.com"
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "lc-reconcile", "python", "reconcile.py"]