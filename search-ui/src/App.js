import React from "react";
import ElasticsearchConnector from "@elastic/search-ui-elasticsearch-connector";
import { 
  SearchProvider, 
  Results,
  SearchBox, 
  Paging, 
  Facet 
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

// Configure the Elasticsearch Connector
const connector = new ElasticsearchConnector({
  // Fallback to localhost if the variable isn't set
  host: process.env.REACT_APP_SEARCH_ENDPOINT || "http://localhost:9200", 
  index: "cv-transcriptions"
});


// (5c) Configure the Search Logic
const config = {
  apiConnector: connector,
  alwaysSearchOnInitialLoad: true, 
  searchQuery: {
    // Fields searchable via the Search Box
    search_fields: {
      generated_text: { weight: 3 },
      duration: { weight: 1 },
      age: { weight: 1 },
      gender: { weight: 1 },
      accent: { weight: 1 }
    },
    // Fields displayed in the Result Cards
    result_fields: {
      generated_text: { snippet: { fallback: true } },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} },
      filename: { raw: {} }
    },
    // Facets for filtering results
    facets: {
      "age.keyword": { type: "value" }, 
      "gender.keyword": { type: "value" },
      "accent.keyword": { type: "value" },
      "duration.keyword": { type: "value" }
    },
    // Ensure default sorting doesn't hit a 'text' field
    sortList: [
      {
        field: "_score",
        direction: "desc"
      }
    ]
  }
};

export default function App() {
  return (
    <SearchProvider config={config}>
      <div className="App">
        <Layout
          header={<SearchBox debounceLength={300} />}
          sideContent={
            <>
              <Facet field="gender.keyword" label="Gender" filterType="any" />
              <Facet field="accent.keyword" label="Accent" filterType="any" />
              <Facet field="age.keyword" label="Age Group" filterType="any" />
              <Facet field="duration.keyword" label="Duration" filterType="any" />
            </>
          }
          bodyContent={
            <Results 
              titleField="filename" 
              shouldTrackClickThrough={true} 
            />
          }
          bodyFooter={<Paging />}
        />
      </div>
    </SearchProvider>
  );
}
