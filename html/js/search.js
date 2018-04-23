var data = {
  "characters": ['Abimanyu', 'Abiyasa', 'Angganjali', 'Anoman', 'Antaboga', 'Antakawulan', 'Antareja', 'Antasena', 'Arimbi', 'Arjuna', 'Asmarawati', 'Badrahini', 'Bagaspati', 'Bagong', 'Baladewa', 'Banowati', 'Bantala', 'Barata', 'Basudewa',
    'Bayu', 'Bendana', 'Bilung', 'Bisawarna', 'Bisma', 'Bismaka', 'Bomanarakasura', 'Brahma', 'Brajadhenta', 'Brajamusthi', 'Citrarata', 'Citrasena', 'Daryamaya', 'Dersanala', 'Desamuka', 'Destarastra', 'Dewa_Ruci', 'Dewaki', 'Dewasrani',
    'Dhadhungawuk', 'Dhamdharat', 'Dhandhang', 'Dhandhonwacana', 'Drupadi', 'Druwasa', 'Durga', 'Durna', 'Duryudana', 'Erawati', 'Gagak_Baka', 'Gareng', 'Garuda', 'Gatotkaca', 'Gendara', 'Gendari', 'Gorawangsa', 'Guru', 'Hagni', 'Indra',
    'Jaya_Bajra', 'Jembawati', 'Kalika', 'Kamajaya', 'Kanastren', 'Kangsa', 'Karna', 'Kartamarma', 'Kartapiyoga', 'Kencana_Wulan', 'Kresna', 'Kumbakarna', 'Kunti', 'Kuntiboja', 'Kurandhayaksa', 'Lesmana_Mandrakumara', 'Lesmana_Murdaka',
    'Madrim', 'Maerah', 'Mandrakeswara', 'Mangsahpati', 'Maruta', 'Nagagini', 'Nagaprasanta', 'Nagatatmala', 'Nakula', 'Narada', 'Nembur_Nawa', 'Ngembat_Landeyan', 'Padmanaba', 'Pancawala', 'Pandu', 'Panyarikan', 'Parasara', 'Petruk',
    'Pracona', 'Pradapa', 'Pragota', 'Pujawati', 'Pulunggana', 'Pulungsari', 'Puntadewa', 'Rama', 'Ramaparasu', 'Ramayadi', 'Ranu', 'Rara_Ireng', 'Ratmuka', 'Rohini', 'Rukmara', 'Rukmini', 'Sadana', 'Sadewa', 'Salya', 'Samba', 'Saragupita',
    'Satrugna', 'Sekipu', 'Semar', 'Sengkuni', 'Setyaboma', 'Setyajid', 'Setyaki', 'Siti_Sendari', 'Soka', 'Sri', 'Sugriwa', 'Suparta', 'Surabramadiraja', 'Surati_Mantra', 'Surtikanthi', 'Surya', 'Tambrapeta', 'Togog', 'TunggulWulung',
    'Udawa', 'Wenang', 'Werkudara', 'Wibisana', 'Wilawuk', 'Wisanggeni', 'Wisnu', 'Wulan_Drema', 'Wulan_Dremi', 'Yamadipati', 'Yamawidura', 'Yuda_Kala_Kresna', 'Yuda_Kothi', 'Yudhistira'
  ],
  "disguised": ['*Amonggati', '*Arjuna', '*Bagus', '*Basudewa', '*Bayu_Bajra', '*Bimasakti', '*Boar', '*Brahala', '*Gatotkaca', '*Godakesa', '*Godhayitma', '*Guard', '*JakaPupon', '*Kalanjaya', '*Kalantaka', '*Kesawasidhi',
    '*Lesmana_Murdaka', '*Lion', '*Nagabanda', '*Nagasewu', '*Narada', '*Nindyamaya', '*Raksasa', '*Raksasa_One', '*Raksasa_Two', '*RaraTemon', '*Resi', '*Sengkalawati', '*Sinduragen', '*Sintawaka', '*SuksmaLanggeng', '*Tiger',
    '*Werkudara', '*Woman'
  ],
  "stories": ["Babad_Wanamarta", "Bandung_Nagasewu", "Basudewa_Grogol", "Brajadhenta_Mbalela_(Gatotkaca_Wisudha)", "Dewa_Ruci", "Gatotkaca_Lahir", "Kunthi_Pilih_(Lahiripun_Adipati_Karna)", "Narayana_Kridha_Brata", "Prabu_Bimasakti",
    "Puntadewa_Wisudha", "Semar_Barang_Jantur", "Semar_Boyong_(Wahyu_Katetreman)", "Semar_Mantu", "Semar_Mantu_Alternative_Version", "Semar_mBangun_Kayangan", "Sudamala", "Suksma_Langgeng", "Wahyu_Cakraningrat", "Wahyu_Kaprawiran",
    "Wahyu_Kembar", "Wahyu_Makutharama", "Wahyu_Topeng_Waja", "Wisanggeni_Lahir"
  ]
};
baseURL = {
  "characters": "characterPages",
  "disguised characters": "characterPages",
  "stories": "lakonPages"
};
typeof $.typeahead === 'function' && $.typeahead({
  input: ".js-typeahead",
  minLength: 1,
  maxItem: 15,
  order: "asc",
  hint: true,
  group: {
    template: "{{group}}"
  },
  maxItemPerGroup: 5,
  backdrop: {
    "background-color": "#fff"
  },
  //href: "../characterPages/{{display}}.html",
  href: function(item) {
    fullURL = rootURL + baseURL[item.group] + "/" + item.display + ".html";
    return fullURL;
  },
  dropdownFilter: "all pages",
  emptyTemplate: 'No result for "{{query}}"',
  source: {
    characters: {
      data: data.characters
    },
    "disguised characters": {
      data: data["disguised"]
    },
    "stories": {
      data: data.stories
    }
  },
  callback: {
    onClickAfter: function(node, a, item, event) {
      // href key gets added inside item from options.href configuration
      //alert(item.href);
      //document.location.href(item.href + ".html");
      //alert(baseURL[item.group]);
    }
  },
  //_options:{href:"null"},
  debug: true
});
