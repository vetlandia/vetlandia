// Estados e principais municípios do Brasil
const BR_STATES = [
  { uf: "AC", name: "Acre" },
  { uf: "AL", name: "Alagoas" },
  { uf: "AP", name: "Amapá" },
  { uf: "AM", name: "Amazonas" },
  { uf: "BA", name: "Bahia" },
  { uf: "CE", name: "Ceará" },
  { uf: "DF", name: "Distrito Federal" },
  { uf: "ES", name: "Espírito Santo" },
  { uf: "GO", name: "Goiás" },
  { uf: "MA", name: "Maranhão" },
  { uf: "MT", name: "Mato Grosso" },
  { uf: "MS", name: "Mato Grosso do Sul" },
  { uf: "MG", name: "Minas Gerais" },
  { uf: "PA", name: "Pará" },
  { uf: "PB", name: "Paraíba" },
  { uf: "PR", name: "Paraná" },
  { uf: "PE", name: "Pernambuco" },
  { uf: "PI", name: "Piauí" },
  { uf: "RJ", name: "Rio de Janeiro" },
  { uf: "RN", name: "Rio Grande do Norte" },
  { uf: "RS", name: "Rio Grande do Sul" },
  { uf: "RO", name: "Rondônia" },
  { uf: "RR", name: "Roraima" },
  { uf: "SC", name: "Santa Catarina" },
  { uf: "SP", name: "São Paulo" },
  { uf: "SE", name: "Sergipe" },
  { uf: "TO", name: "Tocantins" }
];

const BR_CITIES = {
  AC: ["Rio Branco","Cruzeiro do Sul","Sena Madureira","Tarauacá","Feijó","Brasileia","Epitaciolândia","Xapuri","Plácido de Castro","Acrelândia"],
  AL: ["Maceió","Arapiraca","Palmeira dos Índios","Rio Largo","Penedo","União dos Palmares","São Miguel dos Campos","Marechal Deodoro","Coruripe","Delmiro Gouveia","Santana do Ipanema","Murici"],
  AP: ["Macapá","Santana","Laranjal do Jari","Oiapoque","Mazagão","Porto Grande","Tartarugalzinho","Pedra Branca do Amapari"],
  AM: ["Manaus","Parintins","Itacoatiara","Manacapuru","Coari","Tefé","Tabatinga","Maués","Humaitá","Novo Airão","Benjamin Constant","Borba"],
  BA: ["Salvador","Feira de Santana","Vitória da Conquista","Camaçari","Juazeiro","Ilhéus","Itabuna","Lauro de Freitas","Jequié","Barreiras","Alagoinhas","Porto Seguro","Paulo Afonso","Simões Filho","Eunápolis","Teixeira de Freitas","Luís Eduardo Magalhães","Senhor do Bonfim","Itapetinga","Cruz das Almas","Valença","Jacobina"],
  CE: ["Fortaleza","Caucaia","Juazeiro do Norte","Maracanaú","Sobral","Crato","Itapipoca","Maranguape","Iguatu","Quixadá","Canindé","Aquiraz","Russas","Pacatuba","Cascavel","Horizonte","Tianguá","Limoeiro do Norte"],
  DF: ["Brasília","Ceilândia","Taguatinga","Sobradinho","Planaltina","Gama","Samambaia","Águas Claras","Guará","Recanto das Emas","Santa Maria","São Sebastião","Riacho Fundo","Paranoá","Brazlândia","Candangolândia"],
  ES: ["Vitória","Serra","Vila Velha","Cariacica","Linhares","Cachoeiro de Itapemirim","São Mateus","Colatina","Guarapari","Aracruz","Viana","Nova Venécia","Barra de São Francisco"],
  GO: ["Goiânia","Aparecida de Goiânia","Anápolis","Rio Verde","Luziânia","Águas Lindas de Goiás","Valparaíso de Goiás","Trindade","Formosa","Novo Gama","Itumbiara","Senador Canedo","Catalão","Jataí","Planaltina","Caldas Novas","Cidade Ocidental"],
  MA: ["São Luís","Imperatriz","São José de Ribamar","Timon","Caxias","Codó","Paço do Lumiar","Açailândia","Bacabal","Balsas","Santa Inês","Pinheiro","Chapadinha","Barra do Corda"],
  MT: ["Cuiabá","Várzea Grande","Rondonópolis","Sinop","Tangará da Serra","Cáceres","Sorriso","Lucas do Rio Verde","Primavera do Leste","Barra do Garças","Nova Mutum","Alta Floresta"],
  MS: ["Campo Grande","Dourados","Três Lagoas","Corumbá","Grande Dourados","Ponta Porã","Naviraí","Nova Andradina","Aquidauana","Sidrolândia","Maracaju","São Gabriel do Oeste"],
  MG: ["Belo Horizonte","Uberlândia","Contagem","Juiz de Fora","Betim","Montes Claros","Ribeirão das Neves","Uberaba","Governador Valadares","Ipatinga","Sete Lagoas","Divinópolis","Santa Luzia","Ibirité","Poços de Caldas","Patos de Minas","Pouso Alegre","Teófilo Otoni","Barbacena","Sabará","Vespasiano","Conselheiro Lafaiete","Coronel Fabriciano","Ituiutaba","Araguari","Ubá","Muriaé","Passos","Lavras","Formiga","Viçosa","Itabira","João Monlevade","Ouro Preto","Mariana","Araxá"],
  PA: ["Belém","Ananindeua","Santarém","Marabá","Castanhal","Parauapebas","Abaetetuba","Cametá","Altamira","Marituba","Barcarena","Tucuruí","São Félix do Xingu","Paragominas","Itaituba","Redenção","Tailândia"],
  PB: ["João Pessoa","Campina Grande","Santa Rita","Patos","Bayeux","Sousa","Cajazeiras","Cabedelo","Guarabira","Mamanguape","Queimadas","Sapé"],
  PR: ["Curitiba","Londrina","Maringá","Ponta Grossa","Cascavel","São José dos Pinhais","Foz do Iguaçu","Colombo","Guarapuava","Paranaguá","Araucária","Toledo","Apucarana","Pinhais","Campo Largo","Almirante Tamandaré","Umuarama","Cambé","Arapongas","Piraquara","Fazenda Rio Grande","Francisco Beltrão","Paranavaí","Sarandi","Telêmaco Borba","Cianorte","Cornélio Procópio","Irati"],
  PE: ["Recife","Caruaru","Olinda","Petrolina","JABOATÃO DOS GUARARAPES","Paulista","Caruaru","Garca","Gravatá","Cabo de Santo Agostinho","Camaragibe","Garanhuns","Vitória de Santo Antão","Igarassu","Santa Cruz do Capibaribe","São Lourenço da Mata","Abreu e Lima","Carpina","Araripina","Arcoverde","Goiana","Bezerros","Belo Jardim","Timbaúba","Palmares"],
  PI: ["Teresina","Parnaíba","Picos","Piripiri","Floriano","Campo Maior","Barras","União","Pedro II","Altos","Oeiras","São Raimundo Nonato","Corrente","Bom Jesus"],
  RJ: ["Rio de Janeiro","São Gonçalo","Duque de Caxias","Nova Iguaçu","Niterói","Belford Roxo","São João de Meriti","Campos dos Goytacazes","Petrópolis","Volta Redonda","Magé","Itaboraí","Macaé","Cabo Frio","Angra dos Reis","Nova Friburgo","Barra Mansa","Teresópolis","Queimados","Mesquita","Resende","Maricá","Nilópolis","Itaguaí","Guapimirim","Arraial do Cabo","Búzios","Paraty"],
  RN: ["Natal","Mossoró","Parnamirim","São Gonçalo do Amarante","Ceará-Mirim","Caicó","Assu","Macaíba","Santa Cruz","Nova Cruz","Currais Novos","João Câmara"],
  RS: ["Porto Alegre","Caxias do Sul","Pelotas","Canoas","Santa Maria","Gravataí","Viamão","Novo Hamburgo","São Leopoldo","Rio Grande","Alvorada","Passo Fundo","Sapucaia do Sul","Uruguaiana","Santa Cruz do Sul","Cachoeirinha","Bagé","Bento Gonçalves","Erechim","Guaíba","Cachoeira do Sul","Tramandaí","Cruz Alta","Ijuí","Santana do Livramento","Lajeado","Farroupilha","Carlos Barbosa","Vacaria","Venâncio Aires","Camaquã","Sapiranga","Taquara"],
  RO: ["Porto Velho","Ji-Paraná","Ariquemes","Vilhena","Cacoal","Rolim de Moura","Jaru","Guajará-Mirim","Ouro Preto do Oeste","Espigão d'Oeste","Pimenta Bueno"],
  RR: ["Boa Vista","Rorainópolis","Caracaraí","Alto Alegre","Mucajaí","Bonfim","Pacaraima"],
  SC: ["Florianópolis","Joinville","Blumenau","São José","Chapecó","Criciúma","Itajaí","Jaraguá do Sul","Palhoça","Lages","Balneário Camboriú","Brusque","Tubarão","Caçador","Camboriú","Concórdia","São Bento do Sul","Araranguá","Navegantes","Gaspar","Indaial","Rio do Sul","Mafra","Biguaçu","Imbituba","Içara"],
  SP: ["São Paulo","Guarulhos","Campinas","São Bernardo do Campo","Santo André","Osasco","São José dos Campos","Ribeirão Preto","Sorocaba","Mauá","Santos","Mogi das Cruzes","Diadema","Jundiaí","Carapicuíba","Piracicaba","Bauru","Itaquaquecetuba","São José do Rio Preto","Franca","Guarujá","Limeira","Suzano","Taboão da Serra","Praia Grande","Barueri","Americana","São Caetano do Sul","Araraquara","Jacareí","Marília","Presidente Prudente","Araçatuba","Hortolândia","Cotia","Rio Claro","Taubaté","Indaiatuba","Santana de Parnaíba","Sumaré","Botucatu","São Vicente","Ferraz de Vasconcelos","Pindamonhangaba","Guaratinguetá","Itu","Valinhos","Jaguariúna","Caieiras","Votorantim","Atibaia","Bragança Paulista","Itapecerica da Serra","Embu das Artes","Francisco Morato","Cubatão","Sertãozinho","São Carlos","Catanduva","Registro","Ourinhos","Assis"],
  SE: ["Aracaju","Nossa Senhora do Socorro","Lagarto","Itabaiana","Caruaru","São Cristóvão","Estância","Tobias Barreto","Simão Dias","Itaporanga d'Ajuda","Propriá","Mossoró"],
  TO: ["Palmas","Araguaína","Gurupi","Porto Nacional","Paraíso do Tocantins","Araguatins","Colinas do Tocantins","Guaraí","Miracema do Tocantins","Formoso do Araguaia","Dianópolis","Pedro Afonso"]
};

function populateStates(selectEl) {
  selectEl.innerHTML = '<option value="">Selecione o estado...</option>';
  BR_STATES.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.uf;
    opt.textContent = s.name;
    selectEl.appendChild(opt);
  });
}

function populateCities(stateUF, citySelectEl) {
  citySelectEl.innerHTML = '<option value="">Selecione a cidade...</option>';
  const cities = BR_CITIES[stateUF] || [];
  cities.sort().forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    citySelectEl.appendChild(opt);
  });
}

function linkStateCitySelects(stateEl, cityEl) {
  populateStates(stateEl);
  stateEl.addEventListener('change', () => {
    populateCities(stateEl.value, cityEl);
    cityEl.disabled = !stateEl.value;
  });
  cityEl.disabled = true;
}
