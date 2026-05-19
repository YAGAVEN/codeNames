// /media/yagaven_25/coding/Projects/codeNames/src/data/indianWords.js
export const indianWordCategories = {
  Bollywood: [
    'Sholay',
    'Dangal',
    'DDLJ',
    'Jawan',
    'Lagaan',
    'Pathaan',
    'Gully Boy',
    'Kantara',
    'Baahubali',
    'Amitabh'
  ],
  Cricket: [
    'Sachin',
    'Dhoni',
    'Kohli',
    'Wankhede',
    'Eden',
    'IPL',
    'Googly',
    'Yorker',
    'Century',
    'Ranji'
  ],
  'Indian Food': [
    'Biryani',
    'Dosa',
    'Chole',
    'Vada Pav',
    'Rasgulla',
    'Jalebi',
    'Thali',
    'Idli',
    'Paneer',
    'Chai'
  ],
  Cities: [
    'Mumbai',
    'Delhi',
    'Bengaluru',
    'Kolkata',
    'Chennai',
    'Hyderabad',
    'Jaipur',
    'Kochi',
    'Ahmedabad',
    'Pune'
  ],
  Festivals: [
    'Diwali',
    'Holi',
    'Eid',
    'Pongal',
    'Onam',
    'Navratri',
    'Baisakhi',
    'Lohri',
    'Durga Puja',
    'Ganesh'
  ],
  Mythology: [
    'Krishna',
    'Arjuna',
    'Hanuman',
    'Ravana',
    'Ganga',
    'Ayodhya',
    'Kurukshetra',
    'Lakshmi',
    'Shiva',
    'Saraswati'
  ],
  Politics: [
    'Sansad',
    'Rajya Sabha',
    'Lok Sabha',
    'Rashtrapati',
    'Panchayat',
    'Election',
    'Manifesto',
    'Constitution',
    'Governor',
    'Cabinet'
  ],
  'Indian Tech/Startups': [
    'UPI',
    'Aadhaar',
    'ISRO',
    'Infosys',
    'Flipkart',
    'Zomato',
    'Paytm',
    'Ola',
    'Namma Yatri',
    'Chandrayaan'
  ],
  Languages: [
    'Hindi',
    'Tamil',
    'Bengali',
    'Marathi',
    'Telugu',
    'Kannada',
    'Malayalam',
    'Punjabi',
    'Gujarati',
    'Urdu'
  ],
  History: [
    'Ashoka',
    'Akbar',
    'Mughal',
    'Harappa',
    'Nalanda',
    'Dandi',
    'Swaraj',
    'Jallianwala',
    'Vedas',
    'Quit India'
  ]
};

export const indianWords = Object.entries(indianWordCategories).flatMap(([category, words]) =>
  words.map((word, index) => ({
    id: `${category.toLowerCase().replaceAll(/[^a-z0-9]+/g, '-')}-${index}`,
    word,
    category
  }))
);
