
const update_input_field = (element) => {
  const searchBox = document.getElementById('searchBox');
  searchBox.value = `${element.textContent}, `;
}

let input = document.querySelector("#autocomplete #searchBox"),
    ul = document.querySelector("#autocomplete #searchResults"),
    inputTerms, termsArray, prefix, terms, results, sortedResults;


let search = function() {
  inputTerms = input.value.toLowerCase();
  results = [];
  termsArray = inputTerms.split(' ');
  prefix = termsArray.length === 1 ? '' : termsArray.slice(0, -1).join(' ') + ' ';
  terms = termsArray[termsArray.length -1].toLowerCase();
  
  for (let i = 0; i < searchIndex.length; i++) {
    let a = searchIndex[i].toLowerCase(),
        t = a.indexOf(terms);
    
    if (t > -1) {
      results.push(a);
    }
  }
  
  evaluateResults();
};

let evaluateResults = function() {
  if (results.length > 0 && inputTerms.length > 0 && terms.length !== 0) {
    sortedResults = results.sort(sortResults);
    appendResults();
  } 
  else if (inputTerms.length > 0 && terms.length !== 0) {
    ul.innerHTML = '<li>Whoah! <strong>' 
      + inputTerms 
      + '</strong> is not a family member. <br><small><a href="https://google.com/search?q='
      + encodeURIComponent(inputTerms) + '">Try Google?</a></small></li>';
    
  }
  else if (inputTerms.length !== 0 && terms.length === 0) {
    return;
  }
  else {
    clearResults();
  }
};

let sortResults = function (a,b) {
  if (a.indexOf(terms) < b.indexOf(terms)) return -1;
  if (a.indexOf(terms) > b.indexOf(terms)) return 1;
  return 0;
}

const numberOfSuggestion = 10;

let appendResults = function () {
  clearResults();
  
  for (let i=0; i < sortedResults.length && i < 10; i++) {
    let li = document.createElement("li"),
        result = prefix 
          + sortedResults[i].toLowerCase().replace(terms, '<strong>' 
          + terms 
          +'</strong>');
    
    li.innerHTML = result;
    li.addEventListener('click', () => {
      update_input_field(li);
    })
    ul.appendChild(li);
  }

  
  if ( ul.className !== "term-list") {
    ul.className = "term-list";
  }
};

let clearResults = function() {
  ul.className = "term-list hidden";
  ul.innerHTML = '';
};
  
input.addEventListener("keyup", search, false);
