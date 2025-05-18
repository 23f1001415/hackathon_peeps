<template>
    <div>
      <h1>Event Details</h1>
      <p>This is the event detail view for ID: {{ id }}</p>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  
  const props = defineProps({
    id: String
  });
  </script>
  