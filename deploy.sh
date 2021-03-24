#!/bin/bash
git pull && docker-compose -f docker-compose.prod.yml build && docker-compose -f docker-compose.prod.yml down && supervisorctl restart freelanium