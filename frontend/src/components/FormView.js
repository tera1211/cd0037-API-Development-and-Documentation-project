import React, { Component } from 'react';
import $ from 'jquery';
import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props) {
    super();
    this.state = {
      question: '',
      answer: '',
      difficulty: 1,
      category: 1,
      categories: {},
      successMessage:null
    };
  }

  componentDidMount() {
    $.ajax({
      url: `/categories`, //TODO: update request URL
      type: 'GET',
      success: (result) => {
        this.setState({ categories: result.categories });
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again');
        return;
      },
    });
  }

  submitQuestion = (event) => {
    event.preventDefault();
    $.ajax({
      url: '/questions', //TODO: update request URL
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: this.state.difficulty,
        category: this.state.category,
      }),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (result) => {
        document.getElementById('add-question-form').reset();
        this.setState({
          successMessage: 'New question has been successfully created',
        });
        return;
      },
      error: (error) => {
        alert('Unable to add question. Please try your request again');
        return;
      },
    });
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  render() {
    return (
      <div id='add-form'>
        <h2>Add a New Trivia Question</h2>
        {this.state.successMessage && (
          <p className='success-message'>{this.state.successMessage}</p>
        )}
        <form
          className='form-view'
          id='add-question-form'
          onSubmit={this.submitQuestion}
        >
          <div class="form-group">
            <label for="question">Question</label>
            <textarea rows="3" name='question' onChange={this.handleChange} />
          </div>
          <div class="form-group">
            <label for="answer">Answer</label>
            <input type='text' name='answer' onChange={this.handleChange} />
          </div>
          <div class="form-group">
            <label for="difficulty">Difficulty</label>
            <select name='difficulty' onChange={this.handleChange}>
              <option value='1'>1</option>
              <option value='2'>2</option>
              <option value='3'>3</option>
              <option value='4'>4</option>
              <option value='5'>5</option>
            </select>
          </div>
          <div class="form-group">
            <label for="category">Category</label>
            <select name='category' onChange={this.handleChange}>
              {Object.keys(this.state.categories).map((id) => {
                return (
                  <option key={id} value={id}>
                    {this.state.categories[id]}
                  </option>
                );
              })}
            </select>
          </div>
          <input type='submit' className='button' value='Submit' />
        </form>
      </div>
    );
  }
}

export default FormView;
