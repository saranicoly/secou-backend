## Secou? - Backend

#### Execução:
- Dentro de /backend, utilize o comando `uvicorn main:app --reload` para executar o servidor
- É possível acessar o Swagger em `http://127.0.0.1:8000/docs` ou o Redoc em `http://127.0.0.1:8000/redoc`

#### APIs utilizadas:

##### OpenWeather
- OpenWeather é uma api para obtenção de dados climáticos, os dados retornados por ela são:
    - weather (clima)
    - main (temperatura, sensação térmica, minímo e máximo)
    - clouds (% de nuvens)
    - rain (volume de chuvas nas últimas 1h e 3h)
    - visibility (visibilidade)
    - wind (velocidade e força do vento)

Documentação da API: https://openweathermap.org/current

##### Criterios de Alagamento:

Com relação ao código do openWeather:
- Se nao for 2xx, 3xx ou 5xx a chance de alagamentos é zero
