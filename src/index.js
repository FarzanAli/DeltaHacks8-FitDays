import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Tracker from './components/Tracker/Tracker.js';

class Main extends React.Component {

    constructor(props){
        super(props)
    }

    render(){
        return(
            <div className='main-container'>
                <Tracker />
            </div>
        )
    }
}


ReactDOM.render(
    <Main />, document.getElementById('root')
);
