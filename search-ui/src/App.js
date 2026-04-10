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
  host: "http://localhost:9200", 
  index: "cv-transcriptions"
});

// Configure the Search Logic
const config = {
  connector,
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
    // Filters (Facets)
    facets: {
      age: { 
        type: "value",
        size: 10
      },
      gender: { 
        type: "value", 
        sort: "count",
        min_count: 1 
      },
      accent: { 
        type: "value", 
        limit: 10,
        searchable: true
      }
    }
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
              <Facet field="gender" label="Gender" filterType="any" />
              <Facet field="accent" label="Accent" filterType="any" />
              <Facet field="age" label="Age Group" filterType="any" />
              <Facet field="duration" label="Duration" />
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