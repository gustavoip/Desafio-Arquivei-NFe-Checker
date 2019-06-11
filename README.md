# Desafio Arquivei - NFE Checker

Pra rodar 
    ```docker build -t nfe_checker_img . &&  docker run --name nfe_checker  nfe_checker_img```
    
Foi utilizado _Flask_ e _SQLAlchemy ORM_. Por simplicidade o banco utilizado 
foi o _SQLite_, 
mas 
por conta da abstração do _ORM_ poderia ser utilizado qualquer outro banco 
relacional. 
