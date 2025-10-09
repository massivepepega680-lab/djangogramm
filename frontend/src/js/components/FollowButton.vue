<template>
  <div class="d-flex align-items-center">
    <button @click="toggleFollow" :class="buttonClass" :disabled="isLoading">
      {{ buttonText }}
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    profileUsername: { type: String, required: true },
    isInitiallyFollowing: { type: Boolean, required: true },
  },
  data() {
    return {
      isFollowing: this.isInitiallyFollowing,
      isLoading: false,
    }
  },
  computed: {
    buttonText() {
      if (this.isLoading) return '...';
      return this.isFollowing ? 'Unfollow' : 'Follow';
    },
    buttonClass() {
      return this.isFollowing ? 'btn btn-secondary' : 'btn btn-primary';
    },
  },
  methods: {
    toggleFollow() {
      if (this.isLoading) return;
      this.isLoading = true;

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const action = this.isFollowing ? 'unfollow' : 'follow';
      const endpoint = `/users/${this.profileUsername}/${action}/`;
      const originalState = this.isFollowing;
      this.isFollowing = !this.isFollowing;

      axios.post(endpoint, {}, { headers: {'X-CSRFToken': csrfToken} })
      .then(response => {
        console.log(`Successfully performed '${action}' action.`);
        this.$emit('update-follower-count', response.data.follower_count);
      })
      .catch(error => {
        console.error(`Error during '${action}' action, reverting state:`, error);
        this.isFollowing = originalState;
        if (error.response && error.response.status === 403) {
            window.location.href = '/users/login/';
        }
      })
      .finally(() => {
        this.isLoading = false;
      });
    }
  }
}
</script>