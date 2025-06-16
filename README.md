# Strava Analysis 🚴‍♂️📊

Bem-vindo(a) ao **Strava Analysis**, um projeto que une ciclismo e análise de dados!  
Aqui, a proposta é transformar os dados brutos do Strava em informações visuais e acessíveis para ciclistas que desejam acompanhar sua performance de forma mais clara e personalizada.

---

### Motivação

Como ciclista amador e aspirante a analista de dados, sempre senti falta de visualizações mais detalhadas e intuitivas dos meus treinos no Strava. Apesar da plataforma fornecer diversas métricas, percebi que algumas análises poderiam ser melhor aproveitadas, proporcionando ao usuário uma visão mais clara da sua evolução.

Por isso, decidi criar minhas próprias visualizações personalizadas utilizando os dados da API do Strava.

---

### Tecnologias e Etapas

O projeto envolve as seguintes etapas:

- **Autenticação OAuth com Flask**  
  Para garantir o acesso seguro à API do Strava.

- **Coleta de dados com StravaLib**  
  Utilização da biblioteca StravaLib para extrair informações detalhadas dos treinos.

- **Armazenamento em PostgreSQL**  
  Modelagem e criação de um banco de dados PostgreSQL adequado ao cenário de treinos esportivos.

- **Tratamento e injeção de dados**  
  Limpeza, transformação e inserção dos dados coletados no banco.

- **(Em andamento) Dashboards no Power BI**  
  Construção de dashboards interativos para visualização de métricas e evolução dos treinos.

---

### Status

- [x] Autenticação com OAuth (Flask)
- [x] Coleta e tratamento de dados com StravaLib
- [x] Modelagem e integração com PostgreSQL
- [ ] Dashboards interativos no Power BI (em desenvolvimento)

---

### Objetivo

Transformar dados brutos em **informações reais** para quem pedala — de forma **acessível, visual e útil**.

---

### Como contribuir

Sinta-se à vontade para acompanhar, sugerir melhorias ou contribuir com o repositório!

1. Faça um fork do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça o commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça o push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request.

---

### Links

- [Projeto no LinkedIn](https://lnkd.in/egUaVM5X)
- [Documentação da API Strava](https://developers.strava.com/)
