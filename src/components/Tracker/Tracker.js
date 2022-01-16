import React from 'react';
import './tracker.css';

class Tracker extends React.Component{

    constructor(props){
        super(props);
        this.state = {
            steps: 0,
            sleep: 0,
            result: ''
        }
    }

    async componentDidMount(){
        const response = await fetch('http://127.0.0.1:5000/FitBit', {method: 'GET'});
        const data = await response.json();        
        this.setState({steps: data['steps']});
        this.setState({sleep: data['sleep'] + 7});

    }

    async handleRecord(){
        const response = await fetch('http://127.0.0.1:5000/FitBit', {method: 'POST'});
        const data = await response.json();
        console.log(data['result']);
        this.setState({result: data['result']});
    }
    
    render(){
        return(
            <div className='tracker-container'>
                <div className='stats-container'>
                    <div style={{marginBottom: `20px`, fontSize: "60px"}}>FITDAYS</div>
                    <div style={{fontSize: "28px"}}>Fitbit User ID</div><input type="string" style={{border: 'white', height: '30px', borderRadius: '5px', backgroundColor: '', marginBottom: '60px'}} defaultValue={"USER_ID"}>
                    </input>
                    <div>STEPS</div>
                    <div className='value-container'>
                        {this.state.steps}
                    </div>
                    <div>SLEEP</div>
                    <div className='value-container'>
                        {this.state.sleep} Hrs
                    </div>
                    <div className='result-container'>
                        <button className='result-button' onClick={() => this.handleRecord()}>
                            RECORD
                        </button>
                        <div className='result'>
                            {this.state.result}
                        </div>
                    </div>
                </div>
            </div>
        );
        
    }
}

export default Tracker